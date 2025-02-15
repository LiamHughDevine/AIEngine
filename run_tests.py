from retrieve import retrieve

DB_NAME = "test"


def main():
    test_queries = ["Type a document with the name \"History homework\"", "Print the document"]

    for test_query in test_queries:
        context = retrieve(test_query, 4, db_name=DB_NAME)
        print(f"Original Query: {test_query}")
        print("Context:")
        for result in context:
            print(f"Task: {result[0]}")
            print(f"Action: {result[1]}")
        print()


if __name__ == "__main__":
    main()
