import os
import re
from string import letters
import json

import webapp2 
import jinja2

from google.appengine.ext import db 

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>HTML TEMPLATE DIR<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>MAIN HANDLER<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):              #write to browser.*a means this function can take any number of arguments 
      self.response.out.write(*a, **kw)
      
    def render_str(self, template, **params):      #retrieve template 
      t = jinja_env.get_template(template)
      return t.render(params)
    
    def render(self, template, **kw):                #write the retrieved template to the browser
      self.write(self.render_str(template, **kw))

    def render_json(self, d):                      #function for turning a page in json        
      json_txt = json.dumps(d)
      self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
      self.response.out.write(json_txt)
      
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>PARENT BLOG KEY <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#for the future, future blogs with different names 
      
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)      #what is this blogs?    
         
      
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DATABASE/ BLOG ENTRY CLASS<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

class Blog(db.Model):
  subject = db.StringProperty(required = True)
  content  = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)      #each time you add an entry this is set to the time that moment

  
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>FRONT PAGE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  
  
class FrontPage(Handler):
  def render_front(self, subject="", content=""):
      blogsdb = db.GqlQuery("SELECT * FROM Blog "          #refering to Blog class
                             "ORDER BY created Desc limit 10 ")
      self.render("front.html", blogs=blogsdb)
  
  def get(self, subject="", content=""):
      blogsdb = db.GqlQuery("SELECT * FROM Blog "                  #find a way to refer to query: list function?
                             "ORDER BY created Desc limit 10 ")
      if self.request.url.endswith('.json'):
        self.format = 'json'
      else:   
        self.format = 'html'
      if self.format == 'html':
        self.render_front()
      else:   
          jsondict = []                #here we create an empty list and put for loop inside it as have unknown no. of future posts
          for blog in blogsdb:
            time_fmt = '%c'
            d = {'title': blog.subject,'content': blog.content, 'created': blog.created.strftime(time_fmt),   #create this as as_dict function in main handler, as I create a dictionary twice, here and in permalink
                    'last_modified': blog.last_modified.strftime(time_fmt)}         
            jsondict.append(d)  
          self.render_json(jsondict)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> POST Page <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<    
      
class PostPage(Handler):
  def get(self, blog_id):
    blogt = Blog.get_by_id(int(blog_id))      #get the post out of the database
    key = db.Key.from_path('Blog', int(blog_id), parent=blog_key())    #TO DO read up docs for key function 
    if self.request.url.endswith('.json'):
      self.format = 'json'
    else:
      self.format = 'html'  
    if self.format == 'html':   
            self.render('permalink.html', blog = blogt)
    else:
      time_fmt = '%c'
      d = {'title': blogt.subject,'content': blogt.content, 'created': blogt.created.strftime(time_fmt),
                    'last_modified': blogt.last_modified.strftime(time_fmt)}
      self.render_json([d])                #here we put content straight into list as only 1 post (see frontpage)

          
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> NEW POST <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<    
   
class NewPost(Handler):
    def render_newpost(self, subject="", content="", error=""):
      self.render("newpost.html", outtitle=subject, outblog=content, user_error=error)
  
    def get(self):
      self.render_newpost()
      
    def post(self):
      user_title = self.request.get("subject")
      user_blog = self.request.get("content")
      
      if user_title and user_blog:
          blog_post = Blog(subject = user_title, content = user_blog)
          blog_post.put()
          self.redirect('/blog/%s' % str(blog_post.key().id()))
          
      else:
        errortext ="a title and blog please :)"
        self.render_newpost(user_title, user_blog, error = errortext)
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>URL MAPPING<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        
      
app = webapp2.WSGIApplication([('/blog/?', FrontPage),            #/? this means that the last '/'' is optional
                               ('/blog/newpost', NewPost), 
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+).json', PostPage),
                               ('/blog.json', FrontPage),
                               ],
                               debug=True)