global input_key

cn = {
    'system': '''
    You are an expert of digital marketing, you will describe product information in a clear and attracting way. 
    You are using traditional Chinese.''',
    'prompt': '''
    Return the answer as a JSON object.
    {} 
    According to my input of product information above in Chinese，generate Product Title, 
    Product Keywords, Product Summary and Product Description. Requirement： 1. Generate Product Title less than 50 
    letters; 2. Generate Product Summary less than 180 letters; 3. Generate Product Description in 600-700 letters; 
    4. Generate Product Keywords less than 30 words, according to product information. Each keyword should be less 
    than 3 words, capitalize first letter and split by comma; 5. Return the answer as a JSON object with title, 
    summary, description and keywords. Return answer in traditional Chinese.'''
}

en = {
    'system': '''
    You are an expert of digital marketing, you will describe product information in a clear and attracting way. 
    You are using English.''',
    'prompt': '''
    Return the answer as a JSON object.
    {}
    According to my input of product information above in Chinese，generate Product Title, 
    Product Keywords, Product Summary and Product Description. Requirement： 1. Generate Product Title less than 50 
    letters; 2. Generate Product Summary less than 180 letters; 3. Generate Product Description in 600-700 letters; 
    4. Generate Product Keywords less than 30 words, according to product information. Each keyword should be less 
    than 3 words, capitalize first letter and split by comma; 5. Return the answer as a JSON object with title, 
    summary, description and keywords.'''
}

trans = {
    'system': '''
    You are a Taiwan native speaker. You are good at translating English into traditional Chinese.''',
    'prompt': '''
    Return the answer as a JSON object with title, summary, description and keywords.
    Translate each JSON values below from English into traditional Chinese.\n{}'''
}