import re, numpy as np, pandas as pd
import pickle
from xml.dom import minidom
import os
import json
from collections import OrderedDict


def read_data(path):
    """
    Read JSON data from a file.

    Args:
        path (str): The path to the JSON file.

    Returns:
        pandas.DataFrame: A DataFrame containing the JSON data.
    """
    return pd.read_json(path)


def get_words(dat, raw_string):
    """
    Extract words from specified spans in a raw string.

    This function takes a dictionary of spans and a raw string as input. It extracts
    the words covered by the specified spans in the raw string.

    Args:
        dat (dict): A dictionary containing spans for different topics.
            Each topic is a key in the dictionary, and the value is a dictionary
            with 'spans' key containing a list of span tuples (start, end).
        raw_string (str): The raw string from which words will be extracted.

    Returns:
        dict: A dictionary where keys represent topics, and values are
            sets of words extracted from the specified spans in the raw string.
    
    Example:
        dat = {
            'category1': {'spans': [(0, 5), (10, 15)]},
            'category2': {'spans': [(5, 10), (15, 20)]}
        }
        raw_string = "This is a sample raw string."
        result = get_words(dat, raw_string)

        The result will be:
        {
            'category1': {'is', 'This'},
            'category2': {'raw', 'sample'}
        }
    """

    words = {}
    for a in dat.keys():
        semi_words = []
        for b in dat[a]['spans']:
            try:
                semi_words.append(raw_string[b[0]:b[1]])
            except:
                continue
        words[a] = set(semi_words)
    return words


def highlight_words(text, words):
    """
    Highlight specified words in a text with a yellow background.

    This function takes a text and a list of words as input and adds HTML tags to
    highlight the specified words in the set of word with a yellow background color.

    Args:
        text (str): The input text in which words will be highlighted.
        words (list): A set of words to be highlighted in the text.

    Returns:
        str: The input text with specified words highlighted using HTML tags.

    Example:
        text = "This is a sample text containing some keywords."
        words = {'sample', 'keywords'}
        result = highlight_words(text, words)

        The result will be:
        "This is a <span style='background-color:yellow'>sample</span> text containing some <span style='background-color:yellow'>keywords</span>."
    """
    for word in words:
        text = text.replace(word, f"<span style='background-color:yellow'>{word}</span>")
    return text


def save_response(name, label, response_time, document_id, user_id):
    """
    Save annotation response to an XML file.

    This function creates an XML document to store user responses including user name,
    response time, document ID, document label, and user ID. It then saves the XML document
    to a specified directory.

    Args:
        name (str): The user's name or identifier.
        label (str): The document label
        response_time (float): The time taken to complete the annotation.
        document_id (int): The unique ID of the annotated document.
        user_id (int): The unique ID of the user.

    Returns:
        str: The XML document as a string.

    Example:
        name = "user123"
        label = "important"
        response_time = 5.6
        document_id = 12345
        user_id = 9876
        result = save_response(name, label, response_time, document_id, user_id)

        This function will create an XML document with user details, save it to
        "./static/responses/user123/12345.xml", and return the XML document as a string.
    """
    root = minidom.Document()
    xml = root.createElement('root')
    root.appendChild(xml)

    user_name = root.createElement('name')
    user_name.setAttribute("name", name)
    xml.appendChild(user_name)

    response_times = root.createElement('response_time')
    response_times.setAttribute("response_time", str(response_time))
    xml.appendChild(response_times)

    document_ids = root.createElement('document_id')
    document_ids.setAttribute("document_id", str(document_id))
    xml.appendChild(document_ids)

    labels = root.createElement('label')
    labels.setAttribute("label", label)
    xml.appendChild(labels)

    user_ids = root.createElement('user_id')
    user_ids.setAttribute("user_id", str(user_id))
    xml.appendChild(user_ids)

    xml_str = root.toprettyxml(indent ="\t")

    directory = "./static/responses/"+name

    save_path_file = directory + "/"+ str(document_id) +".xml"
    try:
        os.makedirs(directory)
    except:
        print("all_good")
    with open(save_path_file, "w") as f:
        f.write(xml_str)
    return xml_str


def get_texts(topic_list, all_texts, docs):
    """
    Retrieve text data for specified topics and documents.

    Parameters:
    - topic_list (dict): A dictionary containing topics and associated document lists.
    - all_texts (dict): A dictionary containing text data where keys are document IDs and values are corresponding documents.
    - docs (set): A set of document IDs to exclude from the results.

    Returns:
    - results (dict): A dictionary containing text data for specified topics and documents.

    This function takes a 'topic_list' dictionary, which includes topics and associated document lists, an 'all_texts' dictionary containing
    document text data, and a 'docs' set representing documents to exclude. It retrieves text data for specified documents under each topic.
    Docs contain a list of documents that have already been labelled.

    The function returns 'results,' a dictionary where each key represents a topic, and the associated value is a sub-dictionary
    containing document IDs and their corresponding texts for that topic. Documents listed in the 'docs' set are excluded.
    """

    results = {}

    for a in topic_list["cluster"].keys():

        sub_results = {}

        for b in topic_list["cluster"][a]:

            if str(b) in docs:
                continue

            sub_results[str(b)] = all_texts["text"][str(b)]

        results[a]= sub_results
    return results


def get_sliced_texts(topic_list, all_texts, docs):
    """
    Retrieve a maximum number of 6 of text entries from each topic cluster while excluding the 
    documents im docs.
    
    Args:
        topic_list (dict): A dictionary containing topic clusters.
        all_texts (dict): A dictionary of all available text entries.
        docs (list): A list of documents to exclude from extraction.

    Returns:
        dict: A dictionary where keys represent topic clusters, and values are sub-dictionaries
            containing the extracted text entries.

    Example:
        topic_list = {
            "cluster1": [1, 2, 3, 4, 5],
            "cluster2": [6, 7, 8, 9, 10],
            "cluster3": [11, 12, 13, 14, 15]
        }
        all_texts = {
            "text": {
                "1": "Text 1 content",
                "2": "Text 2 content",
                # ...
                "15": "Text 15 content"
            }
        }
        docs = [3, 8]

        result = get_sliced_texts(topic_list, all_texts, docs)

        The result will be a dictionary with limited text entries from each topic cluster:
        {
            "cluster1": {"1": "Text 1 content", "2": "Text 2 content","3": "Text 3 content", "5": "Text 5 content"},
            "cluster2": {"6": "Text 6 content", "7": "Text 7 content", "9": "Text 9 content", "10": "Text 10 content"},
            "cluster3": {"11": "Text 11 content", "12": "Text 12 content", "13": "Text 13 content", "14": "Text 14 content", "15": "Text 15 content"}
        }
    """

    results = {}
    for a in topic_list["cluster"].keys():
        sub_results = {}
        counter = 0
        # print(a, len(topic_list["cluster"][a]))
        if len(topic_list["cluster"][a]) == 0:
            continue
        for b in topic_list["cluster"][a]:
            if str(b) in docs:
                continue
            if counter < 6:
                sub_results[str(b)] = all_texts["text"][str(b)]
            counter+=1
        if len(sub_results) != 0:   
            results[a]= sub_results
    return results 



def get_single_document(top, all_texts, docs):
    """
    Retrieve documents from a collection of texts based on specified topic indices.

    Parameters:
    - top (list or set): A list or set of topic indices to retrieve documents for.
    - all_texts (dict): A dictionary containing text data where keys are topic indices and values are corresponding documents.
    - doc (set): A list of topic indices representing documents that should be excluded from the results.

    Returns:
    - results (dict): A dictionary containing documents for the specified topics that are not in the existing documents set.
    
    This function takes a list  of 'topics' (topic indices), an 'all_texts' dictionary containing text data, and a 'existing_documents' set.
    It iterates through the specified 'topics' and retrieves documents from the 'all_texts' dictionary for topics that are not already in the 'docs' set.

    The function returns a dictionary where each key is a topic index, and the corresponding value is the document text.
    """ 
    results = {}
    for a in top:
        if str(a) in docs:
                continue
        results[str(a)] = all_texts["text"][str(a)]
    return results 


def save_labels(name, document_id, label):
    """
    Save user labels of documents to a JSON file.

    Parameters:
    - session (dict): A dictionary containing user session data, including labels and labeled documents.

    This function reads an existing JSON file containing user data from './static/users/users.json', updates the user's labels
    and labeled document information in the dictionary, and then writes the updated data back to the same JSON file.

    The 'session' dictionary should include the following keys:
    - "name": The user's name or identifier.
    - "labels": A dictionary containing label information.
    - "labelled_document": A dictionary containing information about labeled documents.

    The function does not return any value but updates the JSON file with the modified user data.
    """
    import json

  


    with open('./myapp/static/users/userss.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)

    information[name]['labels']+=" "+str(label)
    information[name]["document_ids"]+=" "+str(document_id)

    with open('./myapp/static/users/userss.json', mode='w', encoding='utf-8') as name_json:
        json.dump(information, name_json, indent=4)



def labelled_docs(labe, all_texts):
    """
    Retrieve labeled documents based on a list of document labels.

    Parameters:
    - labels (str): A comma-separated string of document labels.
    - all_texts (dict): A dictionary containing text data where keys are document labels and values are corresponding documents.

    Returns:
    - results (dict): A dictionary containing documents for the specified labels.

    This function takes a comma-separated string of  'labels' fdrom a particular user (document labels), splits it into individual labels, and retrieves
    documents from the 'all_texts' dictionary based on these labels.

    The function returns a dictionary where each key is a document label, and the corresponding value is the document text.
    If a label is not found in 'all_texts', it is skipped.
    """

    results = {}
    labelled = [x for x in labe.strip().split()]
    for a in labelled:
        try:
            results[a] = all_texts["text"][a]
        except:
            continue
    return results



def extract_label(name, document_id):
    """
    Extract a label attribute from an XML file.

    Parameters:
    - name (str): The name or identifier of the file's owner.
    - number (str): The number or identifier of the XML file.

    Returns:
    - label (str or None): The value of the "label" attribute from the XML file, or None if not found.

    This function constructs the path to an XML file based on the 'name' and 'number' provided, parses the XML file,
    and retrieves the "label" attribute value from the XML's root element.

    Returns the label of the document provided by a user
    """
    import json
    with open('./myapp/static/users/userss.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)[name]
    doc_index = information["document_ids"].strip().split().index(document_id)
    doc_label = information["labels"].strip().split()[doc_index]

 

    
    return doc_label



def completed_json_(name):
    """
    Create a JSON representation of completed documents and document labels for a given user.

    Parameters:
    - name (str): The name of the user whose labeled documents are being processed.

    Returns:
    - completed_json (dict): A JSON-like dictionary representing labeled documents grouped by labels.

    This function processes XML files in a specified directory based on the 'name' provided. It extracts document IDs and labels
    from these XML files and organizes them into a dictionary where labels are keys and associated document IDs are stored in lists.

    The function returns  a dictionary where each key represents a label, and the associated value is a list of
    document IDs labeled with that label.
    """

    import pandas as pd
    import json




def get_recommended_topic(recommended, topics, all_texts):
    """
    Retrieve recommended topic and associated documents from a topic-clustered dataset.

    Parameters:
    - recommended (str): The recommended topic to retrieve.
    - topics (dict): A dictionary containing clustered topics and associated document lists.
    - all_texts (dict): A dictionary containing text data where keys are document IDs and values are corresponding documents.

    Returns:
    - recommended_topic (str): The recommended topic.
    - results (dict): A dictionary containing text data for documents associated with the recommended topic.

    This function takes a 'recommended' topic, a 'topics' dictionary that includes clustered topics and associated document lists,
    and a 'all_texts' dictionary containing document text data. It retrieves text data for documents associated with the specified
    recommended topic.

    The function returns 'recommended_topic,' the name of the recommended topic, and 'results,' a dictionary where each key represents
    a the document IDs of documents within the recommended topic, and the associated value is a sub-dictionary containing document IDs and their corresponding texts.
    """

    results = {}
    for a in topics["cluster"].keys():
        sub_results = {}
        for b in topics["cluster"][a]:
            if b == recommended:
                for c in topics["cluster"][a]:
                    sub_results[str(c)] = all_texts["text"][str(c)]
                results[a] = sub_results
                recommended_topic = a
    return recommended_topic,  results





def save_time(name, page):
    """
    Save the timestamp when a user accesses a specific page to a CSV file.

    Parameters:
    - name (str): The name or identifier of the user.
    - page (str): The name or identifier of the page the user accessed.

    This function appends a new row to a CSV file located in the './static/responses/<name>/time.csv' directory.
    The row contains two columns: 'page' (the accessed page) and 'timestamp' (the current date and time).

    It is used to record when a user accesses different pages and stores the timestamp for future reference.
    """
    from csv import writer
    import datetime
    with open ("./static/responses/"+name+"/time.csv", 'a', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow([page, datetime.datetime.now()])
        f_object.close()


def change_permissions_recursive(path, mode):

    """
    Recursively change permissions (mode) for files and directories under the specified path.

    Parameters:
    - path (str): The root directory path from which to start recursively changing permissions.
    - mode (int): The permission mode to apply (e.g., 0o755 for read, write, and execute for owner, and read and execute for others).

    This function traverses the directory structure starting from the 'path' provided and applies the specified 'mode' to both
    directories and files found within that directory and its subdirectories.
    """
    
    import os
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir, mode)
    for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)


def save_first_time(name, page):
    """
    Save to a CSV file with changed permissions the timestamp when a user first accesses socument page.

    Parameters:
    - name (str): The name or identifier of the user.
    - page (str): The name or identifier of the page the user first accessed.

    This function first recursively changes the permissions of the 'responses' directory and its contents to '0o777'
    (read, write, and execute for everyone) and then appends a new row to a CSV file located in the './static/responses/<name>/time.csv' directory.
    The row contains two columns: 'page' (the accessed page) and 'timestamp' (the current date and time).

    It is used to record when a user first accesses different pages with changed directory permissions to ensure that the user can write to the CSV file.
    """
    from csv import writer
    import datetime
    change_permissions_recursive('./static/responses', 0o777)
    with open ("./static/responses/"+name+"/time.csv", 'w', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow([page, datetime.datetime.now()])
        f_object.close()
    

def make_folder(name):
    """
    Parameters:
    - name (str): The name or identifier of the directory to be created.

    This function creates a new directory with the provided 'name' under the './static/responses/' directory.
    The 'mode' parameter specifies the permission mode for the newly created directory.
    """
    import os
    parent_dir= "./static/responses/"
    mode = 0o666
    path = os.path.join(parent_dir, name)
    os.mkdir(path, mode)


def get_document_data(url, user_id, document_id, all_texts):
    import requests
    import random

    get_document_information =url + "get_document_information"
    response = requests.post(get_document_information, json={ "document_id": document_id,
                                                        "user_id":user_id
                                                         }).json()
    # print(response)

    documenttext = all_texts["text"][str(document_id)]

    
    data = {
        "document": documenttext,
        "user_id":user_id,
        "document_id":document_id,
        }
    

    return data






def append_to_json_file(email, label1, label2, label3, document_id, times, pageTime, manualDoc):
    import os
    import json
    file_path="./annotator/static/users.json"
    try:
    # Ensure the file exists
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump([], file)  # Initialize the file with an empty list

        # Read the existing data
        with open(file_path, 'r') as file:
            existing_data = json.load(file)

        labe = {
            "labels": {
                "first_label":label1,
                "second_label": label2,
                "third_label":label3
            },
            "time": times,
            "label_time": pageTime,
            "document_id": document_id,
            "manual": manualDoc
        }

         

        

        # Append the new data
        # existing_data[email]["label"].append(label)
        existing_data[email]["document_ids"].append(document_id)
        existing_data[email]["labels"][document_id]=labe

        # Write the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(existing_data, file, indent=4)

        print("Successfully submitted")

    except Exception as e:
        print(f"An error occurred while appending to the JSON file: {e}")


def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
         flat_list.extend(row)
    return flat_list


def truncated_data(topics, all_texts, labeled_doc_list ):
    clusters = OrderedDict()
    selected = []
    
    selected_topics = list(topics["cluster"].keys())
    for t in selected_topics:
        clusters[t]=topics["cluster"][t]
        selected.append(topics["cluster"][t])

    selects = flatten_extend(selected)

    keywords = OrderedDict()
    for a in selected_topics:
        keywords[a] = topics["keywords"][a]

    all_text = OrderedDict()
    for b in selects:
        if int(b) not in labeled_doc_list:

            try:
                all_text[b]=all_texts["text"][str(b)]
            except:
                continue
    # recommended = list(all_text.keys())[0]
        

        

    return all_text, keywords, clusters


def sort_labeled(all_texts, all_labeled):
    filteredTexts = {}
    for text in  all_labeled:
        filteredTexts[str(text)] = all_texts['text'][str(text)]

    return filteredTexts


    




    

def get_all_labeled(email):
    user_json = json.load(open("./annotator/static/users.json"))
    first_label = {}
    for a, b in user_json[email]["labels"].items():
        first_label[b['labels']['first_label']]=[]

    for a, b in user_json[email]["labels"].items():
        first_label[b['labels']['first_label']].append(a)  

    return first_label

import random

def manual_function():
        return "True" if random.random() < 0.35 else "False"