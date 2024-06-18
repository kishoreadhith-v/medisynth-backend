import datetime
from flask import jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['dev-db']
forum_collection = db['forum']

# create a new post
def create_post(data):
    post = {
        'forum_id': data.get('forum_id'),
        'title': data.get('title'),
        'content': data.get('content'),
        'author': data.get('author'),
        'created_at': datetime.datetime.now(),
        'comments': [],
        'upvotes': 0,
    }
    result = forum_collection.insert_one(post)
    return str(result.inserted_id)

# get posts by forum id, select 15 random posts from the collection each time, but make sure that have already been selected are not selected again
def get_posts(selected_posts):
    posts = []
    for post in forum_collection.find({'forum_id': selected_posts}):
        posts.append({
            'id': str(post['_id']),
            'title': post['title'],
            'content': post['content'],
            'author': post['author'],
            'created_at': post['created_at'],
            'comments': post['comments'],
            'upvotes': post['upvotes']
        })
    return posts

#comment on a post
def comment_on_post(post_id, comment):
    forum_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$push': {'comments': comment}}
    )
    return 'Comment added successfully'

# get a post by id
def get_post(post_id):
    post = forum_collection.find_one({'_id': ObjectId(post_id)})
    return {
        'id': str(post['_id']),
        'title': post['title'],
        'content': post['content'],
        'author': post['author'],
        'created_at': post['created_at'],
        'comments': post['comments'],
        'upvotes': post['upvotes']
    }

# delete a post by id
def delete_post(post_id):
    forum_collection.delete_one({'_id': ObjectId(post_id)})
    return 'Post deleted successfully'

# delete a comment by id
def delete_comment(post_id, comment_id):
    forum_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$pull': {'comments': {'_id': ObjectId(comment_id)}}}
    )
    return 'Comment deleted successfully'

# update a post by id
def update_post(post_id, data):
    forum_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$set': data}
    )
    return 'Post updated successfully'

# search for a post by title
def search_post(title):
    posts = []
    for post in forum_collection.find({'title': {'$regex': title, '$options': 'i'}}):
        posts.append({
            'id': str(post['_id']),
            'title': post['title'],
            'content': post['content'],
            'author': post['author'],
            'created_at': post['created_at'],
            'comments': post['comments'],
            'upvotes': post['upvotes']
        })
    return posts

# upvote a post
def upvote_post(post_id):
    forum_collection.update_one(
        {'_id': ObjectId(post_id)},
        {'$inc': {'upvotes': 1}}
    )
    return 'Post upvoted successfully'


