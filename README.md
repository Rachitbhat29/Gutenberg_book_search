# Gutenberg_book_search

Simple api for search for books info avaiable in Gutenberg Repository


#To start app:
python app.py

#Add postgres db and load datadump
Db Config details:
db_host = 'localhost'
db_user = 'postgres'
db_password = 'admin'
db_port = 5432
db_name = 'Book_Repo_Db'



The API support the following:
● Retrieval of books meeting zero or more filter criteria. Each query return the
following:
  ○ The number of books meeting the criteria
  ○ A list of book objects, each of which contains the following:
      ■ Title of the book
      ■ Information about the author
      ■ Genre
      ■ Language
      ■ Subject(s)
      ■ Bookshelf(s)
      ■ A list of links to download the book in the available formats (mime-types)
      
      
      
 Applicable Rules:
○ In case the number of books that meet the criteria exceeds 25, the API 
  return only 25 books at a time with pageno and it support the means of retrieving the next sets
  of 25 books till all books are retrieved by adding the page no in to the prameters.
○ The books are returned in decreasing order of popularity, as measured by
  the number of downloads. 
○ Data returned in a JSON format.
○ Multiple filter criteria permitted in each API call and multiple filter
  values allowed for each criteria. e.g. an API call should be able to filter
  on ‘language=en,fr’ and ‘topic=child, infant’.



Filters avaiable:
○ Book ID numbers specified as Project Gutenberg ID numbers.
○ Language
○ Mime-type
○ Topic. Topic should filter on either ‘subject’ or ‘bookshelf’ or both. Case
insensitive partial matches should be supported. e.g. ‘topic=child’ should among
others, return books from the bookshelf ‘Children’s literature’ and from the
subject ‘Child education’.
○ Author. Case insensitive partial matches should be supported.
○ Title. Case insensitive partial matches should be supported.


Example:

Url : http://127.0.0.1:5000/book_info?language=en%2Cfr&page=2

Output: 

{
  "no_of_books": 26,
  "page_no": "2",
  "per_page": 25,
  "total_pages": 2,
  "books_info": [
    [
      {
        "title": "The Kama Sutra of Vatsyayana: Translated From the Sanscrit in Seven Parts With Preface, Introduction and Concluding Remarks",
        "author_name": [
          "Vatsyayana"
        ],
        "author_birthyr": [
          null
        ],
        "author_deathyr": [
          null
        ],
        "genre": [
          ""
        ],
        "languages": [
          "en"
        ],
        "subjects": [
          "Love",
          "Sex"
        ],
        "bookshelves": [
          "Banned Books from Anne Haight's list",
          "Erotic Fiction",
          "Sociology"
        ],
        "url": [
          "http://www.gutenberg.org/ebooks/27827.epub.images",
          "http://www.gutenberg.org/ebooks/27827.kindle.noimages",
          "http://www.gutenberg.org/ebooks/27827.rdf",
          "http://www.gutenberg.org/ebooks/27827.txt.utf-8",
          "http://www.gutenberg.org/files/27827/27827-8.txt",
          "http://www.gutenberg.org/files/27827/27827-h/27827-h.htm",
          "http://www.gutenberg.org/files/27827/27827.txt",
          "http://www.gutenberg.org/files/27827/27827.zip"
        ]
      }
    ]
  ]
}


  
 
