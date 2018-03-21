from peewee import Model, AutoField, CharField, Proxy, ForeignKeyField, DoesNotExist, IntegerField, FloatField

db = Proxy()


class BaseModel(Model):
    class Meta:
        database = db


class Mesh(BaseModel):
    id = AutoField(unique=True, primary_key=True)
    domain = CharField(null=True)
    decision_criteria = IntegerField(null=True)

    @staticmethod
    def set_domain(mesh_id, domain, decision_criteria):
        Mesh.update(domain=domain, decision_criteria=int(decision_criteria)).where(Mesh.id == mesh_id).execute()

    class Meta:
        table_name = 'meshes'


class Node(BaseModel):
    id = AutoField()
    node_id = CharField(unique=True)
    mesh_id = ForeignKeyField(Mesh, backref='nodes')
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    @staticmethod
    def get_domain(node_id):
        try:
            node_db_entry = Node.select().where(Node.node_id == node_id).get()
        except DoesNotExist:
            return None
        return node_db_entry.mesh_id.domain

    @staticmethod
    def get_mesh_id(node_id):
        try:
            node_db_entry = Node.select().where(Node.node_id == node_id).get()
        except DoesNotExist:
            return None
        return node_db_entry.mesh_id.id

    @staticmethod
    def get_location(node_id):
        try:
            node_db_entry = Node.select().where(Node.node_id == node_id).get()
        except DoesNotExist:
            return None
        return {"latitude": node_db_entry.latitude, "longitude": node_db_entry.longitude}

    class Meta:
        table_name = 'mesh_members'