def text_to_list(text):
    list = text.split(',')
    cleaned_list = [chunk.strip() for chunk in list]
    return cleaned_list

text = 'a  , b , c, d'
print(text_to_list(text))