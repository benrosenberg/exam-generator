# exam generator
yaml + python + pandoc + latex => exam PDF

## process

1. write exam questions and answers into special format yaml file
2. python converts txt file into pandoc md file, with chosen args
3. pandoc converts md to a PDF for questions and a different one for answers

see the example in `example.yml` for details on how to format your file. all yaml arguments are optional.

## running

run `python parser.py` in the directory with your `.yml` or `.yaml` file.