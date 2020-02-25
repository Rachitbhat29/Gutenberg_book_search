#!/usr/bin/env python
###########################################################################
##
##  Simple Flask-based REST API and example search books for data from Project Gutenberg
##
##  Author:  Rachit Bhatnagar <rachit.bhat29@gmail.com>
##  Date:    22 Feb 2020
##
##  References:
##    - http://docs.sqlalchemy.org/en/latest/orm/query.html
##        #sqlalchemy.orm.query.Query.filter
##    - http://docs.sqlalchemy.org/en/latest/orm/internals.html
##        #sqlalchemy.orm.attributes.QueryableAttribute.like
##    - http://www.unixwiz.net/techtips/sql-injection.html
##
##
###########################################################################


from flask import Flask, request
from flask_restplus import Api, Resource, fields
import psycopg2
from itertools import islice

def create_app():
    app = Flask(__name__)
    api = Api(app, title='Gutenberg Books Info',
              description='Simple api for search for books info avaiable in Gutenberg')

    book_format = api.model('Book_info', {'id':fields.Integer('Book ID numbers'),
                                          'language':fields.String('Languages'),
                                          'mime-type':fields.String('Mime-type'),
                                          'topic':fields.String('Topic'),
                                          'author':fields.String('Author Name'),
                                          'title':fields.String('Book Title'),
                                          'page':fields.Integer('Page Number')})

    query1 = """SELECT to_json(t) FROM
    ("""
    query2 = """select title, json_agg(distinct a.name) as Author_name, json_agg(distinct a.birth_year) as  Author_birthyr, 
    json_agg(distinct a.death_year) as Author_Deathyr,
    json_agg(distinct SUBSTRING(s.name,(length(s.name)-POSITION('-' in reverse(s.name))+3),length(s.name))) as Genre,
    json_agg(distinct l.code) as languages, json_agg(distinct s.name) as Subjects, 
    json_agg(distinct bsh.name) as Bookshelves, 
    json_agg(distinct f.url) as url
    from books_book b left join books_book_authors ba on b.id = ba.book_id
    left join books_author a on a.id = ba.author_id 
    left join books_book_languages bl on b.id = bl.book_id
    left join books_language l on l.id = bl.language_id 
    left join books_book_subjects bs on b.id = bs.book_id
    left join books_subject s on s.id = bs.subject_id
    left join books_book_bookshelves bbsh on b.id = bbsh.book_id
    left join books_bookshelf bsh on bsh.id = bbsh.bookshelf_id
    left join books_format f on f.book_id = b.id """

    query3 = """ GROUP by title, b.download_count
    order by b.download_count DESC
    limit 26) t"""

    final_query = ''
    pageno = 1 #Default page no.


    @api.route('/book_info')
    class ReturnJson(Resource):

        @api.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' },
                 params={'id': 'Book ID numbers specified as Project Gutenberg ID numbers',
                         'language': 'Languages like en,fr etc.',
                         'mime-type': 'Mime-type',
                         'topic': 'Topic should filter on either ‘subject’ or ‘bookshelf’ or both.',
                         'author': 'Author Name',
                         'title': 'Book Title',
                         'page': 'Page Number'
                         })
        def get(self):
            c = connect_db()
            if c:
                cur = c.cursor()
                cur.execute(get_no_of_books())
                fetchrows = cur.fetchall()
                close_db(cur)
                totallen = len(fetchrows)
                global pageno
                if pageno == '1':
                    pageno = int(pageno)
                    new_res= take(0,25, fetchrows)
                else:
                    new_res = take((int(pageno)-1) * 25 , (int(pageno)-1) * 25  +25, fetchrows)

                print((int(pageno)-1) * 25 ,(int(pageno)-1) * 25  +25)
                response = ({'no_of_books': totallen, 'page_no': pageno, 'per_page': 25, 'total_pages':int(totallen//25 +1),
                            'books_info': new_res})

                # parsed = json.loads(dict({'no_of_books': len(fetchrows), 'books_info':fetchedrow}))
                return response, 200
            return "<h1>Hello World</h1>"


    def get_no_of_books():
        """Return no. of books for all avaiable filters"""
        filters = ''
        filters_sql = ''
        global final_query
        final_query = ''
        limit = 25

        if request.args:
            args = dict(request.args)

            global pageno
            pageno= args.get('page')
            print(pageno)
            if not pageno:
                pageno = 1
            del args['page']

            def add_to_filter(fil,filters=''):
                """ Function to prepare query to add filtere with 'in' condition """
                if fil is not None:
                    print(fil)
                    if len(fil) > 0:
                        fil_l = fil.split(',')
                        for i in fil_l:
                            filters += str("'" + i + "'") + ','
                            # print(filters, fil.__name__)
                        filters = filters[:-1]     # removing lsat comma
                        return filters # returning complete clause
                return None

            def add_to_filter_like(fil,filters=''):
                """ Function to prepare query to add filtere with 'like' condition """
                if fil is not None:
                    print(fil)
                    fil_l = fil.split(',')
                    for i in fil_l:
                        filters += str(i) + '|'
                    # print(filters, fil.__name__)
                    filters = filters[:-1]     # removing last '|'
                    print(filters)
                    if not filters.find('|'):
                        return filters
                    else:
                        return str("("+filters+")") # returning complete clause
                return None

            while args:
                """Loop to all available filters"""
                if 'language' in args:
                    languages = args.get('language')
                    filters_sql += str("l.code in (" + add_to_filter(languages) + ")")
                    del args['language']
                    filters_sql += ' AND '
                if 'title' in args:
                    titles = request.args.get('title')
                    filters_sql += str("lower(title) similar to lower('%" + add_to_filter_like(titles) + "%')")
                    del args['title']
                    filters_sql += ' AND '
                if 'id' in args:
                    id = args.get('id')
                    filters_sql += str("gutenberg_id in (" + add_to_filter(id) + ")")
                    del args['id']
                    filters_sql += ' AND '
                if 'mime-type' in args:
                    mimetype = args.get('mime-type')
                    filters_sql += str("mime-type in (" + add_to_filter(mimetype) + ")")
                    del args['mime-type']
                    filters_sql += ' AND '
                if 'author' in args:
                    authors = args.get('author')
                    filters_sql += str("lower(a.name) similar to lower('%" + add_to_filter_like(authors) + "%')")
                    del args['author']
                    filters_sql += ' AND '
                if 'topic' in args:
                    topics = args.get('topic')
                    filters_sql += str("(lower(s.name) similar to lower ('%" + add_to_filter_like(topics) + "%') "
                                       "or lower(bsh.name) similar to lower('%" +
                                       add_to_filter_like(topics) + "%')) ")
                    del args['topic']
                    filters_sql += ' AND '


        print(filters_sql)
        if filters_sql[-4:] == 'AND ':
            filters_sql = filters_sql[:-4]
        if filters_sql is not None:
            filters_sql = ' where ' + filters_sql
        if filters_sql.endswith('where '):
            filters_sql= filters_sql[:-6]

        final_query = query1+query2+filters_sql+query3
        print(final_query)
        return final_query

    def connect_db():
        c = psycopg2.connect("postgresql://postgres:admin@localhost/Book_Repo_Db")
        return c

    # @app.teardown_request
    def close_db(c):
        c.close()

    def take(n,l,iterable):
        "Return first n items of the iterable as a list"
        return list(islice(iterable,n,l))

    return  app

# if __name__ == '__main__':
#     app.run(debug=True)