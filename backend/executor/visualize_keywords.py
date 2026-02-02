import os
import random
import pandas as pd
import pickle
import sys

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from constant import CATEGORY_KEYWORDS_PICKLE_FILE, KEYWORDS_PER_NEWS_PICKLE_FILE
except ImportError:
    CATEGORY_KEYWORDS_PICKLE_FILE = "data/category_keywords.pkl"
    KEYWORDS_PER_NEWS_PICKLE_FILE = "data/keyword_per_news.pkl"

def load_data():
    if not os.path.exists(CATEGORY_KEYWORDS_PICKLE_FILE):
        print(f"❌ {CATEGORY_KEYWORDS_PICKLE_FILE} not found!")
        category_keywords = {}
    else:
        category_keywords = pd.read_pickle(CATEGORY_KEYWORDS_PICKLE_FILE)

    if not os.path.exists(KEYWORDS_PER_NEWS_PICKLE_FILE):
        print(f"❌ {KEYWORDS_PER_NEWS_PICKLE_FILE} not found!")
        news_keywords = {}
    else:
        news_keywords = pd.read_pickle(KEYWORDS_PER_NEWS_PICKLE_FILE)

    return category_keywords, news_keywords

def show_list_options(options):
    mapping = {}
    for i, name in enumerate(options, start=1):
        print(f"{i}. {name}")
        mapping[str(i)] = name
    return mapping

def show_category_keywords(category_keywords):
    print("\n📋 Categories:")
    mapping = show_list_options(list(category_keywords.keys()))
    
    choice = input("\nEnter category name or number: ").strip()
    category = mapping.get(choice, choice)
    
    if category in category_keywords:
        print(f"\n🏷️  Top keywords for category {category.upper()}:")
        print("-" * 50)
        for term, score in category_keywords[category]:
            print(f"{term:<20} | TF-IDF: {score}")
        print("-" * 50)
    else:
        print("Category not found!")

def show_news_keywords(news_keywords):
    while True:
        print("\n===================================")
        print("   📰 News Keyword Analysis")
        print("===================================\n")

        all_ids = list(news_keywords.keys())
        if not all_ids:
            print("No news keywords available.")
            return

        # Show 5 random news IDs
        random_ids = random.sample(all_ids, min(5, len(all_ids)))

        print("🎲 Random available news IDs:")
        for i, nid in enumerate(random_ids, start=1):
            print(f"{i}. {nid}")

        print("\n📌 Options:")
        print("1️⃣  View keywords for the 5 news items above")
        print("2️⃣  Select specific news item by ID")
        print("3️⃣  Return to main menu")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            for nid in random_ids:
                print(f"\n📝 Top keywords for news {nid}:")
                print("-" * 50)
                if nid in news_keywords:
                    for term, score in news_keywords[nid][:10]:
                        print(f"{term:<20} | TF-IDF: {score}")
                else:
                    print("⚠️ Not found in database.")
                print("-" * 50)

        elif choice == "2":
            nid = input("Enter News ID: ").strip()
            if nid in news_keywords:
                print(f"\n📝 Top keywords for news {nid}:")
                print("-" * 50)
                for term, score in news_keywords[nid][:10]:
                    print(f"{term:<20} | TF-IDF: {score}")
                print("-" * 50)
            else:
                print("❌ News ID not found!")

        elif choice == "3":
            return
        else:
            print("❌ Invalid choice!")

def main():
    category_keywords, news_keywords = load_data()
    
    while True:
        print("\n===================================")
        print("  🔍 Vietnamese News Keyword Analysis")
        print("===================================")
        print("1️⃣  Keywords by Category")
        print("2️⃣  Keywords by News Item")
        print("3️⃣  Exit")
        
        choice = input("\nChoice: ").strip()
        if choice == "1":
            show_category_keywords(category_keywords)
        elif choice == "2":
            show_news_keywords(news_keywords)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
