
from flask import Blueprint

test = Blueprint('test',__name__,url_prefix='/')

@test.route('/',methods=['GET'])
def conexion():
    return 'Servidor online...'
