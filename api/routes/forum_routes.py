from flask import Blueprint, request, jsonify
from controllers.forum_controller import create_post, get_posts, comment_on_post, get_post, delete_post, delete_comment, upvote_post, update_post, search_post

forum_bp = Blueprint('forum', __name__, url_prefix='/forum')

@forum_bp.route('/create_post', methods=['POST'])
def create():
    data = request.json
    return jsonify(create_post(data))

@forum_bp.route('/get_posts', methods=['GET'])
def get():
    selected_posts = request.json
    return jsonify(get_posts(selected_posts=selected_posts))

@forum_bp.route('/comment_on_post', methods=['POST'])
def comment():
    data = request.json
    return jsonify(comment_on_post(data))

@forum_bp.route('/get_post/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    return jsonify(get_post(post_id))

@forum_bp.route('/delete_post/<post_id>', methods=['DELETE'])
def delete(post_id):
    return jsonify(delete_post(post_id))

@forum_bp.route('/delete_comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    return jsonify(delete_comment(comment_id))

@forum_bp.route('/upvote_post/<post_id>', methods=['PUT'])
def upvote(post_id):
    return jsonify(upvote_post(post_id))

@forum_bp.route('/update_post/<post_id>', methods=['PUT'])
def update(post_id):
    data = request.json
    return jsonify(update_post(post_id, data))

@forum_bp.route('/search_post', methods=['GET'])
def search():
    query = request.args.get('query')
    return jsonify(search_post(query))