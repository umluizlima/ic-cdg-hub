from flask import (
    jsonify, request
)
from app.models import (
    db, Item, Category
)
from app.api.errors import (
    bad_request, internal_server, not_found
)
from app.api import api
from app.api.controllers.auth import token_required


@api.route('/items', methods=['POST'])
@token_required
def create_item():
    data = request.get_json() or {}

    error = Item.check_data(data=data, new=True)
    if 'registry' in data and data['registry'] is not None and \
            Item.query.filter_by(registry=data['registry']).first():
        error = 'tombo já existe'
    if 'category_id' in data and data['category_id'] is not None and \
            Category.query.get(data['category_id']) is None:
        error = 'categoria não existe'
    if error:
        return bad_request(error)

    item = Item()
    item.from_dict(data)

    try:
        db.session.add(item)
        db.session.commit()
    except Exception:
        return internal_server()

    return jsonify(item.to_dict()), 201


@api.route('/items', methods=['GET'])
@token_required
def get_available_items():
    return jsonify(
        [item.to_dict() for item in Item.query.filter(Item.available)]
    )


@api.route('/items/all', methods=['GET'])
@token_required
def get_all_items():
    return jsonify(
        [item.to_dict() for item in Item.query.all()]
    )


@api.route('/items/<int:id>', methods=['GET'])
@token_required
def get_item(id: int):
    item = Item.query.filter_by(id=id).first()
    if item is None:
        return not_found('item não encontrado')
    return jsonify(item.to_dict())


@api.route('/items/<int:id>', methods=['PUT'])
@token_required
def update_item(id: int):
    item = Item.query.filter_by(id=id).first()
    if item is None:
        return not_found('item não encontrado')

    data = request.get_json() or {}

    error = Item.check_data(data=data)
    if 'registry' in data and data['registry'] is not None \
            and data['registry'] != item.registry and \
            Item.query.filter_by(registry=data['registry']).first() is not None:
        error = 'tombo já existe'
    if 'category_id' in data and data['category_id'] is not None and \
            Category.query.get(data['category_id']) is None:
        error = 'category_id não existe'
    if error:
        return bad_request(error)

    item.from_dict(data)
    try:
        db.session.commit()
    except Exception:
        return internal_server()

    return jsonify(item.to_dict())


@api.route('/items/<int:id>', methods=['DELETE'])
@token_required
def delete_item(id: int):
    item = Item.query.filter_by(id=id).first()
    if item is None:
        return not_found('item não encontrado')

    try:
        db.session.delete(item)
        db.session.commit()
    except Exception:
        return internal_server()

    return '', 204
