#!/usr/bin/env python3
"""
Script to add missing posts handlers to lambda_handler_auth_posts.py
"""

def add_missing_handlers():
    """Add missing handler functions to the file"""
    
    # Read the current file
    with open('lambda_handler_auth_posts.py', 'r') as f:
        content = f.read()
    
    # Find the position to insert the missing handlers
    # Look for the end of handle_create_post function
    insert_pos = content.find('    except Exception as e:\n        logger.error(f"Create post error: {e}")\n        return create_error_response(500, "INTERNAL_ERROR", "Create post failed")')
    
    if insert_pos == -1:
        print("Could not find insertion point")
        return
    
    # Find the end of the exception block
    insert_pos = content.find('        return create_error_response(500, "INTERNAL_ERROR", "Create post failed")', insert_pos)
    insert_pos = content.find('\n', insert_pos) + 1
    
    # The missing handlers code
    missing_handlers = '''
async def handle_get_posts(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle get posts request."""
    try:
        query_params = event.get("queryStringParameters") or {}
        
        # Build query parameters
        query_params_dynamo = {}
        
        if query_params.get("subreddit_id"):
            query_params_dynamo["subredditId"] = query_params["subreddit_id"]
        
        if query_params.get("author_id"):
            query_params_dynamo["authorId"] = query_params["author_id"]
        
        if query_params.get("post_type"):
            query_params_dynamo["postType"] = query_params["post_type"]
        
        # Query posts
        if query_params_dynamo:
            response = posts_table.scan(
                FilterExpression=" AND ".join([f"{k} = :{k}" for k in query_params_dynamo.keys()]),
                ExpressionAttributeValues={f":{k}": v for k, v in query_params_dynamo.items()},
                Limit=int(query_params.get("limit", 20))
            )
        else:
            response = posts_table.scan(Limit=int(query_params.get("limit", 20)))
        
        posts = response.get("Items", [])
        
        # Sort posts
        sort_by = query_params.get("sort_by", "created_at")
        sort_order = query_params.get("sort_order", "desc")
        
        if sort_by == "created_at":
            posts.sort(key=lambda x: x.get("createdAt", ""), reverse=(sort_order == "desc"))
        elif sort_by == "score":
            posts.sort(key=lambda x: x.get("score", 0), reverse=(sort_order == "desc"))
        
        # Get author usernames
        for post in posts:
            try:
                user_response = users_table.get_item(Key={"userId": post["authorId"]})
                post["authorUsername"] = user_response.get("Item", {}).get("username", "Unknown")
            except:
                post["authorUsername"] = "Unknown"
        
        # Create response
        post_responses = []
        for post in posts:
            post_responses.append(PostResponse(
                post_id=post["postId"],
                title=post["title"],
                content=post["content"],
                author_id=post["authorId"],
                author_username=post["authorUsername"],
                subreddit_id=post["subredditId"],
                post_type=post["postType"],
                url=post["url"],
                media_urls=post["mediaUrls"],
                score=post["score"],
                upvotes=post["upvotes"],
                downvotes=post["downvotes"],
                comment_count=post["commentCount"],
                view_count=post["viewCount"],
                created_at=post["createdAt"],
                updated_at=post["updatedAt"],
                is_deleted=post.get("isDeleted", False),
                is_locked=post.get("isLocked", False),
                is_sticky=post.get("isSticky", False),
                is_nsfw=post.get("isNsfw", False),
                is_spoiler=post.get("isSpoiler", False),
                flair=post["flair"],
                tags=post["tags"],
                awards=post["awards"]
            ).dict())
        
        return create_success_response(
            data={
                "posts": post_responses,
                "total_count": len(post_responses),
                "has_more": False,
                "next_offset": None
            },
            message="Posts retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return create_error_response(500, "INTERNAL_ERROR", "Get posts failed")

'''
    
    # Insert the missing handlers
    new_content = content[:insert_pos] + missing_handlers + content[insert_pos:]
    
    # Write the updated file
    with open('lambda_handler_auth_posts.py', 'w') as f:
        f.write(new_content)
    
    print("Added missing handle_get_posts function")

if __name__ == "__main__":
    add_missing_handlers()
