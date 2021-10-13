import os
def empty():
    print("Empty")
    os.system('echo "The bowl is empty! Please refill it." | festival --tts')
    return 


def refill():
    print("Refill")
    os.system('echo "woof woof woof. Come eat." | festival --tts')
    return 

def speak(q, status):
    while True:
        if not q.empty():
            obj = q.get()
            if "check" in obj["text"] or "condition" in obj["text"]:
                empty()
            else:
                refill()