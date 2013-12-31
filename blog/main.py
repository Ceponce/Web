#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    #returns a string of that rendered template
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    #writes a string from render_str
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#we will define our database now
class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class NewPost(Handler):
    def render_front(self, subject="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("front.html", subject=subject, content=content, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = Blog(subject=subject, content=content)
            a.put()

            self.redirect("/newpost")

        else:
            error = "we need both a title and some artwork!"
            self.render_front(subject, content, error)


class MainPage(NewPost):
    def render_front(self, subject="", content="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")

        self.render("posts.html", subject=subject, content=content, error=error, blogs=blogs)

class BlogPost(NewPost):
    def get(self, blog_id):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        subject=""
        content=""
        for blog in blogs:
            if blog.key().id()==int(blog_id):
                subject=blog.subject
                content=blog.content

        self.render("post.html", subject=subject, content=content)

application = webapp2.WSGIApplication([
    ('/', MainPage),('/newpost', NewPost),('/([0-9]+)', BlogPost)],
debug = True)

