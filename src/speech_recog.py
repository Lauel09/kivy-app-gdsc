import spacy
import logging

class MedicineRecognizer:
    meds_scanned = [
    ]
    def __init__(self):
        self.nlp = spacy.load("en_ner_bc5cdr_md")
        logging.info("Successfully loaded the model")

    def extract_medicine_name(self, sentence):
        doc = self.nlp(sentence)
        for ent in doc.ents:
            self.meds_scanned.append(ent.text)
        logging.info(f"Medicines scanned: {self.meds_scanned}")

