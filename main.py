import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

t_base = jinja_env.get_template("base.html")

class BlogPost(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)

    # def render(self):
    #     self._render_text = self.content.replace('\n','<br>')
    #     return render_str("post.html", p=self)

class Handler(webapp2.RequestHandler):

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class MainHandler(webapp2.RequestHandler):
    def get(self):

        lastfive = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")

        t_frontpage=jinja_env.get_template("frontpage.html")
        response = t_base.render(
                    title = "Michael Cowan's Blog",
                    content = t_frontpage.render(lastfive=lastfive))
        self.response.write(response)

class NewPost(webapp2.RequestHandler):
    def get(self):
        t_newpost = jinja_env.get_template("newpost.html")
        newPost = t_newpost.render(postTitle="",error_postTitle="",postContent="",error_postContent="")
        response = t_base.render(
                    title="Create New Post",
                    content=newPost)
        self.response.write(response)

    def post(self):
        errorflag=False
        post_title = self.request.get('postTitle')
        post_content = self.request.get('postContent')

        error_title = ""
        error_content = ""

        if (not post_title) or (post_title == ""):
            errorflag=True
            error_title = "Please add a Blog Post Title"

        if (not post_content) or (post_content == ""):
            errorflag=True
            error_content="Please add Blog Post Content"

        post_title=cgi.escape(post_title, quote=True)
        post_content=cgi.escape(post_content, quote=True)

        if errorflag:
            t_newpost=jinja_env.get_template("newpost.html")
            newPost=t_newpost.render(postTitle=post_title,error_postTitle=error_title,postContent=post_content,error_postContent=error_content)
            response = t_base.render(
                    title = "Create New Post",
                    content = newPost)
            self.response.write(response)
        else:
            blogpost = BlogPost(title=post_title, body=post_content)
            blogpost.put()
            post_id=blogpost.key().id()
            post_id=str(post_id)
            self.redirect('/blog/'+post_id)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, post_id):
        # key=db.Key.from_path('Post', int(post_id), parent=db.Key.from_path('blogs','default'))
        # post=db.get(key)

        post=BlogPost.get_by_id(int(post_id))

        if not post:
            self.error(404)
            return

        #blogpost=post.get_by_id

        t_permalink=jinja_env.get_template("permalink.html")
        response = t_base.render(
                    title = "Michael Cowan's Blog",
                    content = t_permalink.render(blogpost=post))
        self.response.write(response)

app = webapp2.WSGIApplication([
    ('/blog/', MainHandler),
    ('/newpost/', NewPost),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
], debug=True)
