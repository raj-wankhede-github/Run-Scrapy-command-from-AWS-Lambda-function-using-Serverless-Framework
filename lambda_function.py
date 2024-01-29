import sys
import subprocess

def handler(event, context):
    # Run the Scrapy spider
    print(event)
    print("Scrapy running now")
    subprocess.run(["scrapy", "crawl", "fooddive"])
    subprocess.run(["scrapy", "crawl", "news"])
    print("Scrapy ran successfully")
    return { 
        'statusCode': '200',   # a valid HTTP status code
        'body': 'Lambda function invoked',        
    }
