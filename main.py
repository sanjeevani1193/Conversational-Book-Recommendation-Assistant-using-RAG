from src.query_parser import rewrite_query_with_llm


def main():
    user_query = "an innocent girl falls in love with a dangerous mobster but I want emotional depth"
    parsed_query = rewrite_query_with_llm(user_query)
    print(parsed_query)


if __name__ == "__main__":
    main()