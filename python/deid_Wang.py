import re
import sys
phone_pattern ='(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'

# compiling the reg_ex would save sime time!
ph_reg = re.compile(phone_pattern)


# hospital_file = open("/deid2020/lists/stripped_hospitals.txt")
# hospotal_list = [line.rstrip('\n') for line in hospital_file]
# for hospital in hospotal_list:
#     hospital.rstrip()
#     alias1 = hospital.replace('&','').replace('\'','').replace('-','').rstrip()
#     if alias1 not in hospotal_list:
#         hospotal_list.append(alias1)
#     if 'hospital' in hospital.lower():
#         alias = hospital.lower().replace('hospital','').rstrip()
#         alias2 = alias.lower().replace('&','').replace('\'','').replace('-','').rstrip()
#         hospotal_list.append(alias)
#         if alias2 not in hospotal_list:
#             hospotal_list.append(alias2)


# def check_hospital(patient,note,chunk, output_handle):
#     output_handle.write('Patient {}\tNote {}\n'.format(patient,note))
#     new_chunk = chunk.lower()
    
#     for hospital in hospotal_list:
#         index = new_chunk.find(hospital.lower())
#         if index == -1:
#             continue
#         result = chunk[index:len(hospital)]
#         output_handle.write(result+'\n')

def check_dateyear(patient,note,chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function. 
    Logic:
        Search the entire chunk for phone number occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find phones.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27
    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))
    #split the record into words 
    new_chunk = chunk.lower().split(' ')
    #strip off the ending whitespaces
    new_chunk = [x.rstrip() for x in new_chunk]

    #go through each word in the record, to see if it is an integer
    for word in new_chunk:
        word = word.rstrip()
        #if the length of the word is bigger than 2 (to avoid index error), get rid of the starting and ending symbols
        if len(word)>=2:
            if word[-1] is '.' or word[-1] is ';' or word[-1] is ',' or word[-1] is ')':
                word = word[:-1]
            if word[0] is '\'' or word[0] is '(':
                word = word[1:]   
        
        #if the cleaned word is an integer, then if it between 1900-2020 or 90-100, consider them as potentially date year
        if word.isdigit():
            word_int = int(word)
            if  (word_int >=1900 and word_int <=2020) or (word_int<100 and word_int > 90):
                start_index = str(chunk.lower().find(word)-offset)
                end_index = str(chunk.lower().find(word)+len(word)-offset)
                # create the string that we want to write to file ('start start end') 
                result =start_index +' '+start_index +' '+end_index
                # write the result to one line of output
                output_handle.write(result+'\n')
            
            # if word_int <10 and word[0] is not '0':
            #     continue
            
            # if word_int >=10 and word_int<=60:
            #     continue
            
            

        



def check_for_phone(patient,note,chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function. 
    Logic:
        Search the entire chunk for phone number occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find phones.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in ph_reg.finditer(chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
            print((match.start()-offset),match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')

            
            
def deid_phone(text_path= 'id.text', output_path = 'phone.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each phone number found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected phone number string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no phone number detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each phone number detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end phone_number
        where `start` is the start position of the detected phone number string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    
    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # open the output file just once to save time on the time intensive IO
    with open(output_path,'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_phone(patient,note,chunk.strip(), output_file)
                    check_dateyear(patient,note,chunk.strip(), output_file)
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_phone(sys.argv[1], sys.argv[2])
    
# Examining "DateYear" category.


# ==========================

# Num of true positives = 24

# Num of false positives = 157

# Num of false negatives = 22

# Sensitivity/Recall = 0.0

# PPV/Specificity = 0.0
