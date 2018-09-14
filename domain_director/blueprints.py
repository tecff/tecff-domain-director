import json
from flask import Blueprint, request, current_app, jsonify, render_template
from ipaddress import AddressValueError
from mozls import WifiNetwork, query_mls, MLSException

from domain_director import ipv6_to_mac
from domain_director.db import Node
from domain_director.domain import decide_node_domain

bp = Blueprint('domain_director', __name__)


@bp.route('/', methods=['GET', 'POST'])
def serve():
    revisit = False
    domain = None
    is_vpn_only = False

    wifis = request.form["wifis"]
    try:
        mls_response = query_mls(
            wifi_networks=[WifiNetwork(mac_address=ap["bssid"], signalStrength=int(ap["signal"]))
                           for ap in json.loads(wifis)],
            apikey=current_app.config["MLS_API_KEY"])
    except MLSException:
        mls_response = None
    try:
        ip_address = request.headers.get("X-Real-IP", None) or request.remote_addr
        node_id = ipv6_to_mac(ip_address).replace(':', '')
        is_vpn_only = len(list(Node.select().where(Node.mesh_id == Node.get_mesh_id(node_id)))) == 1
        domain = decide_node_domain(node_id=node_id,
                                    lat=mls_response.lat if mls_response else None,
                                    lon=mls_response.lon if mls_response else None,
                                    accuracy=mls_response.accuracy if mls_response else None,
                                    polygons=current_app.domain_polygons,
                                    default_domain=current_app.config["DEFAULT_DOMAIN"])
        if domain == current_app.config["DEFAULT_DOMAIN"]:
            revisit = True
    except AddressValueError:
        revisit = True
    return jsonify({
        "node_information": {
            "location": {"lat": mls_response.lat,
                         "lon": mls_response.lon,
                         "accuracy": mls_response.accuracy, },
            "domain": {
                "name": domain if domain else current_app.config["DEFAULT_DOMAIN"],
                "switch_time": -1 if current_app.config["ONLY_MIGRATE_VPN"] and not is_vpn_only
                else current_app.config["DOMAIN_SWITCH_TIME"],
                "revisit": revisit, }
        }})


@bp.route('/nodes', methods=['GET'])
def list_nodes():
    return render_template("nodes.html", meshes=Node.get_nodes_grouped())


@bp.route('/nodes.json', methods=['GET'])
def list_nodes_json():
    return jsonify(Node.get_nodes_grouped())
