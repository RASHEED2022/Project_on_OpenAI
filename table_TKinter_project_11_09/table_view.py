import tkinter as tk
from tkinter import ttk
import json

def table():
    def sub_keywords(item,keywords):
      for keyword in keywords:
        if isinstance(keyword, dict):
            # Subtopic found, create a new item
            subtopic_name = list(keyword.keys())[0] #sub topic name
            subtopic_data = keyword[subtopic_name] #description and keywords
            subtopic_item = tree.insert(item, "end", text=subtopic_name)
            keywords = subtopic_data.get("keywords", [])
            sub_keywords(subtopic_item,keywords)
        else: 
          tree.insert(item, "end", text=keyword)


    def toggle_subtopics(event):
        item = tree.focus()
        if item:
            children = tree.get_children(item)
            if children:
                # If there are children, hide them
                tree.delete(*children)
            else:
                # If no children, display the subtopics or keywords
                topic = tree.item(item, "text")
                # print(topic)
                if topic in data:
                    keywords = data[topic].get("keywords", [])
                    tree.bind("<Double-1>", sub_keywords)
                    sub_keywords(item,keywords)

    # Load data from the "response.json" file
    try:
        with open("output.json", "r") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = {}

    # Create the main window
    root = tk.Tk()
    root.title("Table View")
    root.config(padx=50,pady=30,bg="#94A684")

    # Set a custom window size (width x height)
    window_width = 800
    window_height = 600
    root.geometry(f"{window_width}x{window_height}")

    # Create a TreeView widget
    tree = ttk.Treeview(root)
    tree.pack(fill=tk.BOTH, expand=True)  # Fill the available space

    # Insert main topics into the tree
    for topic in data.keys():
        tree.insert("", "end", text=topic)

    # Bind the toggle_subtopics function to double-click event
    tree.bind("<Double-1>", toggle_subtopics)

    root.mainloop()
# table()
