from bs4 import BeautifulSoup

def get_text(xml):
        html = BeautifulSoup(xml, 'lxml')
            entries = html.find_all('span')
                text = ""
                    
                        for entry in entries:
                                    line = entry.get_text()
                                            line = process_line(line)
                                                    
                                                            if line is not None:
                                                                            text += line
                                                                                
                                                                                    return text

                                                                                def process_line(line):
                                                                                        line = re.sub('[\n\r]+', ' ', line)
                                                                                            line = line.strip()
                                                                                                
                                                                                                    if len(line) == 0:
                                                                                                                return None
