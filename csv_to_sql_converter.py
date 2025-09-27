#!/usr/bin/env python3
"""
Script per convertire i dati CSS Challenge da CSV a database SQL
con tipi di dati appropriati, pulizia dei dati e traduzione in inglese.
"""

import pandas as pd
import sqlite3
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Any
import warnings

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HealthcareDataConverter:
    def __init__(self, db_path: str = "healthcare_data_english.db"):
        """
        Inizializza il convertitore con percorso del database
        
        Args:
            db_path: Percorso del file database SQLite
        """
        self.db_path = db_path
        self.conn = None
        
        # Dizionario traduzioni dal tedesco all'inglese
        self.translations = {
            # Age groups
            '0-10 Jahre': '0-10 Years',
            '10-20 Jahre': '10-20 Years', 
            '20-30 Jahre': '20-30 Years',
            '30-40 Jahre': '30-40 Years',
            '40-50 Jahre': '40-50 Years',
            '50-60 Jahre': '50-60 Years',
            '60-70 Jahre': '60-70 Years',
            '70-80 Jahre': '70-80 Years',
            '80-90 Jahre': '80-90 Years',
            '90+ Jahre': '90+ Years',
            
            # Reasons for treatment
            'Krankheit': 'Illness',
            'Unfall': 'Accident',
            'Mutterschaft': 'Maternity',
            'Prävention': 'Prevention',
            'Vorsorge': 'Preventive Care',
            'Nachsorge': 'Follow-up Care',
            
            # Healthcare provider main groups
            'Spitäler': 'Hospitals',
            'SpitÃ¤ler': 'Hospitals',  # Handle encoding issues
            'Ärzte und Ärztinnen': 'Doctors',
            'Ã„rzte und Ã„rztinnen': 'Doctors',  # Handle encoding issues
            'Laboratorien': 'Laboratories',
            'Pflegeheime': 'Nursing Homes',
            'Apotheken': 'Pharmacies',
            'Physiotherapie': 'Physiotherapy',
            'Ergotherapie': 'Occupational Therapy',
            'Psychologie': 'Psychology',
            'Zahnärzte': 'Dentists',
            'Optiker': 'Opticians',
            'Abgabestellen Mittel und Gegenstände': 'Medical Device Dispensing Points',
            'Chiropraktoren und Chiropraktorinnen': 'Chiropractors',
            'Ergotherapeuten und Ergotherapeutinnen': 'Occupational Therapists',
            'Ernährungsberater und Ernährungsberaterinnen': 'Nutritional Counselors',
            'Fitness': 'Fitness',
            'Hebammen': 'Midwives',
            'Komplementärtherapeuten und -therapeutinnen': 'Complementary Therapists',
            'Logopäden und Logopädinnen': 'Speech Therapists',
            'Neuropsychologen und Neuropsychologinnen': 'Neuropsychologists',
            'Organisationen der Krankenpflege & Hilfe zu Hause': 'Nursing & Home Care Organizations',
            'Pflegefachmänner und Pflegefachfrauen': 'Professional Nurses',
            'Physiotherapeuten und Physiotherapeutinnen': 'Physiotherapists',
            'Podologen und Podologinnen': 'Podologists',
            'Psych. Psychotherapeuten und Psychotherapeutinnen': 'Psychological Psychotherapists',
            'Transport-/Rettungsunternehmen': 'Transport/Rescue Companies',
            'Übrige Rechnungssteller': 'Other Billing Entities',
            
            # Healthcare provider types (extended)
            'Zentrumsversorgung, Niveau 1': 'Central Care, Level 1',
            'Zentrumsversorgung, Niveau 2': 'Central Care, Level 2',
            'Zentrumsversorgung, Niveau 3': 'Central Care, Level 3',
            'Zentrumsversorgung, Niveau 4': 'Central Care, Level 4',
            'Zentrumsversorgung, Niveau 5': 'Central Care, Level 5',
            'Zentrumsversorgung': 'Central Care',
            'Grundversorgung': 'Basic Care',
            'Spezialisierte Psychiatrie': 'Specialized Psychiatry',
            'Psychiatrische Kliniken': 'Psychiatric Clinics',
            'Rehabilitation': 'Rehabilitation',
            'Gruppenpraxen': 'Group Practices',
            'Einzelpraxen': 'Individual Practices',
            'Gemeinschaftspraxen': 'Community Practices',
            'Polikliniken': 'Polyclinics',
            'Tageskliniken': 'Day Clinics',
            'Ambulatorien': 'Outpatient Clinics',
            'Notfallzentren': 'Emergency Centers',
            'Universitätsspitäler': 'University Hospitals',
            'Regionalspitäler': 'Regional Hospitals',
            'Kantonsspitäler': 'Cantonal Hospitals',
            'Privatspitäler': 'Private Hospitals',
            'Spezialkliniken': 'Specialty Clinics',
            'Spezialkliniken Chirurgie': 'Surgical Specialty Clinics',
            'Pflegeheime': 'Nursing Homes',
            'Privatlaboratorien': 'Private Laboratories',
            'Mikrobiologie/Genetik-Laboratorien': 'Microbiology/Genetics Laboratories',
            'Mikrobiologie-Laboratorien': 'Microbiology Laboratories',
            'Organisationen der Apotheker und Apothekerinnen': 'Pharmacy Organizations',
            'Organisationen der Krankenpflege & Hilfe zu Hause': 'Nursing & Home Care Organizations',
            'Physiotherapeuten und Physiotherapeutinnen': 'Physiotherapists',
            'Chiropraktoren und Chiropraktorinnen': 'Chiropractors',
            'Psych. Psychotherapeuten und Psychotherapeutinnen': 'Psychological Psychotherapists',
            'praktischer Arzt / Ärztin': 'General Practitioner',
            'Ärzte, Spezialfälle': 'Doctors, Special Cases',
            'Übrige Rechnungssteller': 'Other Billing Entities',
            'Übrige Rechnungssteller, Spezialfälle': 'Other Billing Entities, Special Cases',
            'Abgabestellen Mittel und Gegenstände': 'Medical Device Dispensing Points',
            'Akut- und Übergangspflege': 'Acute and Transitional Care',
            'Alters- und Pflegeheime': 'Elderly and Nursing Homes',
            'Apotheken, Spezialfälle': 'Pharmacies, Special Cases',
            'Blutspendezentren': 'Blood Donation Centers',
            'Diverse Spezialkliniken': 'Various Specialty Clinics',
            'Ergotherapeuten und Ergotherapeutinnen': 'Occupational Therapists',
            'Ergotherapiezentren': 'Occupational Therapy Centers',
            'Ernährungsberater und Ernährungsberaterinnen': 'Nutritional Counselors',
            'Ernährungsberatung, Organisation': 'Nutritional Counseling, Organization',
            'Fitness': 'Fitness',
            'Geburtshäuser': 'Birth Centers',
            'Gemeinsame Einrichtung KVG': 'Joint Health Insurance Institution',
            'Genetik-Laboratorien': 'Genetics Laboratories',
            'Grundversorgung, Niveau 3': 'Basic Care, Level 3',
            'Grundversorgung, Niveau 4': 'Basic Care, Level 4',
            'Grundversorgung, Niveau 5': 'Basic Care, Level 5',
            'Hebammen': 'Midwives',
            'Heime für Behinderte': 'Homes for Disabled',
            'Komplementärtherapeuten und -therapeutinnen': 'Complementary Therapists',
            'Logopäden und Logopädinnen': 'Speech Therapists',
            'Neuropsychologen und Neuropsychologinnen': 'Neuropsychologists',
            'Organisationen der Chiropraktik': 'Chiropractic Organizations',
            'Organisationen der Hebammen': 'Midwife Organizations',
            'Organisationen der Krankenpflege & Hilfe zu Hause AÜP': 'Nursing & Home Care Organizations AÜP',
            'Organisationen der Krankenpflege & Hilfe zu Hause TON': 'Nursing & Home Care Organizations TON',
            'Organisationen der Logopädie': 'Speech Therapy Organizations',
            'Organisationen der Neuropsychologie': 'Neuropsychology Organizations',
            'Organisationen der Physiotherapie': 'Physiotherapy Organizations',
            'Organisationen der Podologie': 'Podology Organizations',
            'Organisationen der psychologischen Psychotherapie': 'Psychological Psychotherapy Organizations',
            'Pflegefachmänner und Pflegefachfrauen': 'Professional Nurses',
            'Pflegeheime, Spezialfälle (ohne BUR-Zurodnung)': 'Nursing Homes, Special Cases (without BUR assignment)',
            'Podologen und Podologinnen': 'Podologists',
            'Prävention und Gesundheitswesen': 'Prevention and Public Health',
            'Psychiatrische Kliniken, Niveau 1': 'Psychiatric Clinics, Level 1',
            'Psychiatrische Kliniken, Niveau 2': 'Psychiatric Clinics, Level 2',
            'Rehabilitationskliniken': 'Rehabilitation Clinics',
            'Spezialkliniken Geriatrie': 'Geriatric Specialty Clinics',
            'Spezialkliniken Pädiatrie': 'Pediatric Specialty Clinics',
            'Spitäler, Spezialfälle (ohne BUR-Zuordnung)': 'Hospitals, Special Cases (without BUR assignment)',
            'Tages- oder Nachtstrukturen TON': 'Day or Night Structures TON',
            'Transport-/Rettungsunternehmen, Spezialfälle': 'Transport/Rescue Companies, Special Cases',
            'Zentrumsversorgung, Niveau 1 (Universitätsspitäler)': 'Central Care, Level 1 (University Hospitals)',
            'Diabetesgesellschaften': 'Diabetes Societies',
            
            # Medical specialties (extended)
            'Kinder- und Jugendmedizin': 'Pediatrics',
            'Kinder- und Jugendpsychiatrie und -psychotherapie': 'Child and Adolescent Psychiatry and Psychotherapy',
            'Gynäkologie und Geburtshilfe': 'Gynecology and Obstetrics',
            'GynÃ¤kologie und Geburtshilfe': 'Gynecology and Obstetrics',  # Handle encoding issues
            'Psychiatrie und Psychotherapie': 'Psychiatry and Psychotherapy',
            'Chirurgie': 'Surgery',
            'Innere Medizin': 'Internal Medicine',
            'Allgemeine Innere Medizin': 'General Internal Medicine',
            'Radiologie': 'Radiology',
            'Anästhesiologie': 'Anesthesiology',
            'Dermatologie': 'Dermatology',
            'Dermatologie und Venerologie': 'Dermatology and Venereology',
            'Ophthalmologie': 'Ophthalmology',
            'Orthopädie': 'Orthopedics',
            'Neurologie': 'Neurology',
            'Urologie': 'Urology',
            'HNO': 'ENT (Ear, Nose, Throat)',
            'Oto-Rhino-Laryngologie': 'Otorhinolaryngology (ENT)',
            'Kardiologie': 'Cardiology',
            'Onkologie': 'Oncology',
            'Endokrinologie': 'Endocrinology',
            'Rheumatologie': 'Rheumatology',
            'Nephrologie': 'Nephrology',
            'Pneumologie': 'Pneumology',
            'Gastroenterologie': 'Gastroenterology',
            'Hämatologie': 'Hematology',
            'Infektiologie': 'Infectious Diseases',
            'Notfallmedizin': 'Emergency Medicine',
            'Allgemeinmedizin': 'General Medicine',
            'Hausarztmedizin': 'Family Medicine',
            'Tropenmedizin': 'Tropical Medicine',
            'Arbeitsmedizin': 'Occupational Medicine',
            'Sportmedizin': 'Sports Medicine',
            'Geriatrie': 'Geriatrics',
            'Palliativmedizin': 'Palliative Medicine',
            'Intensivmedizin': 'Intensive Care Medicine',
            'Nuklearmedizin': 'Nuclear Medicine',
            'Pathologie': 'Pathology',
            'Rechtsmedizin': 'Forensic Medicine',
            'Labormedizin': 'Laboratory Medicine',
            'Mikrobiologie': 'Microbiology',
            'Immunologie': 'Immunology',
            'Genetik': 'Genetics',
            'Toxikologie': 'Toxicology',
            'Pharmakologie': 'Pharmacology',
            'Hygiene': 'Hygiene',
            'Epidemiologie': 'Epidemiology',
            'Biostatistik': 'Biostatistics',
            'Physikalische Medizin und Rehabilitation': 'Physical Medicine and Rehabilitation',
            'Allergologie und klinische Immunologie': 'Allergology and Clinical Immunology',
            'Angiologie': 'Angiology',
            'Arbeitsmedizin': 'Occupational Medicine',
            'Gefässchirurgie': 'Vascular Surgery',
            'Handchirurgie': 'Hand Surgery',
            'Herz- und thorakale Gefässchirurgie': 'Cardiac and Thoracic Vascular Surgery',
            'Infektiologie': 'Infectious Diseases',
            'Intensivmedizin': 'Intensive Care Medicine',
            'Kiefer- und Gesichtschirurgie': 'Oral and Maxillofacial Surgery',
            'Kinderchirurgie': 'Pediatric Surgery',
            'Klinische Pharmakologie und Toxikologie': 'Clinical Pharmacology and Toxicology',
            'Medizinische Genetik': 'Medical Genetics',
            'Medizinische Onkologie': 'Medical Oncology',
            'Neurochirurgie': 'Neurosurgery',
            'Orthopädische Chirurgie und Traumatologie des Bewegungsapparates': 'Orthopedic Surgery and Traumatology of the Locomotor System',
            'Plastische, Rekonstruktive und Ästhetische Chirurgie': 'Plastic, Reconstructive and Aesthetic Surgery',
            'Radio-Onkologie und Strahlentherapie': 'Radio-Oncology and Radiation Therapy',
            'Tropen- und Reisemedizin': 'Tropical and Travel Medicine',
            
            # Other healthcare services
            'Spitex': 'Home Care',
            'Ambulante Pflege': 'Outpatient Care',
            'Stationäre Pflege': 'Inpatient Care',
            'Langzeitpflege': 'Long-term Care',
            'Kurzzeitpflege': 'Short-term Care',
            'Tagespflege': 'Day Care',
            'Nachtpflege': 'Night Care',
            'Palliativpflege': 'Palliative Care',
            'Hospiz': 'Hospice',
            'Diabetesberatung': 'Diabetes Counseling',
            'Ernährungsberatung': 'Nutritional Counseling',
            'Sozialberatung': 'Social Counseling',
            'Psychologische Beratung': 'Psychological Counseling',
            'Seelsorge': 'Pastoral Care',
            'Logopädie': 'Speech Therapy',
            'Podologie': 'Podology',
            'Osteopathie': 'Osteopathy',
            'Chiropraktik': 'Chiropractic',
            'Homöopathie': 'Homeopathy',
            'Naturheilkunde': 'Naturopathy',
            'Akupunktur': 'Acupuncture',
            'Massage': 'Massage',
            'Fitness': 'Fitness',
            'Wellness': 'Wellness',
            
            # Gender terms
            'M': 'Male',
            'F': 'Female',
            'W': 'Female',
            'männlich': 'Male',
            'weiblich': 'Female',
            
            # Common German words that might appear
            'und': 'and',
            'oder': 'or',
            'mit': 'with',
            'ohne': 'without',
            'für': 'for',
            'von': 'from',
            'zu': 'to',
            'in': 'in',
            'an': 'at',
            'auf': 'on',
            'bei': 'at',
            'nach': 'after',
            'vor': 'before',
            'über': 'about',
            'unter': 'under',
            'durch': 'through',
            'um': 'around',
            'gegen': 'against',
            'zwischen': 'between',
        }
        
        # Definizione tipi di dati corretti per ogni colonna
        self.dtype_mapping = {
            'patient_id': 'VARCHAR(50)',
            'age': 'VARCHAR(20)',  # es. "20-30 Years" (translated)
            'gender': 'VARCHAR(10)', # Male/Female (translated)
            'reason_for_treatment': 'VARCHAR(100)',
            'healthcare_provider_id': 'VARCHAR(50)',
            'healthcare_provider_type': 'TEXT',
            'healthcare_provider_main_group': 'VARCHAR(100)',
            'client_id': 'VARCHAR(50)',
            'client_type': 'TEXT',
            'client_main_group': 'VARCHAR(100)',
            'start_date': 'DATE',
            'end_date': 'DATE',
            'tariff': 'VARCHAR(3)',  # Sempre 3 caratteri dopo pulizia
            'tariff_position': 'VARCHAR(50)',
            'quantity': 'REAL'
        }
        
        # Tipi pandas per caricamento CSV
        self.pandas_dtypes = {
            'patient_id': 'string',
            'age': 'string',
            'gender': 'string',
            'reason_for_treatment': 'string',
            'healthcare_provider_id': 'string',
            'healthcare_provider_type': 'string',
            'healthcare_provider_main_group': 'string',
            'client_id': 'string',
            'client_type': 'string',
            'client_main_group': 'string',
            'start_date': 'string',  # Convertiremo a datetime dopo
            'end_date': 'string',    # Convertiremo a datetime dopo
            'tariff': 'string',      # Puliremo dopo caricamento
            'tariff_position': 'string',
            'quantity': 'float64'
        }
        
        # Colonne da tradurre
        self.columns_to_translate = [
            'age',
            'gender', 
            'reason_for_treatment',
            'healthcare_provider_type',
            'healthcare_provider_main_group',
            'client_type',
            'client_main_group'
        ]

    def translate_text(self, text: str) -> str:
        """
        Traduce un testo dal tedesco all'inglese usando il dizionario
        """
        if pd.isna(text) or text is None:
            return text
            
        text_str = str(text).strip()
        
        # Cerca traduzione diretta
        if text_str in self.translations:
            return self.translations[text_str]
        
        # Cerca traduzioni parziali (per testi composti)
        translated_parts = []
        for part in text_str.split():
            if part in self.translations:
                translated_parts.append(self.translations[part])
            else:
                translated_parts.append(part)
        
        return ' '.join(translated_parts) if translated_parts else text_str

    def translate_column(self, series: pd.Series, column_name: str) -> pd.Series:
        """
        Traduce un'intera colonna pandas dal tedesco all'inglese
        """
        logger.info(f"Traduzione colonna '{column_name}' in corso...")
        
        # Prima mostra alcuni esempi di traduzioni
        unique_values = series.dropna().unique()[:10]
        logger.info(f"Esempi traduzioni per '{column_name}':")
        
        translated_series = series.apply(self.translate_text)
        
        for orig, trans in zip(unique_values, translated_series[series.isin(unique_values)].unique()[:10]):
            if orig != trans:
                logger.info(f"  '{orig}' -> '{trans}'")
        
        return translated_series

    def clean_tariff_codes(self, tariff_series: pd.Series) -> pd.Series:
        """
        Pulisce i codici tariff per assicurarsi che siano tutti stringhe a 3 cifre:
        - Rimuove .0 dai float (es. "312.0" -> "312")  
        - Aggiunge padding di zeri a sinistra per codici corti (es. "99" -> "099", "1" -> "001")
        """
        def clean_single_tariff(value):
            if pd.isna(value):
                return None
                
            # Converti a stringa
            str_value = str(value).strip()
            
            # Rimuovi .0 se presente
            if str_value.endswith('.0'):
                str_value = str_value[:-2]
            
            # Gestisci caso 'nan'
            if str_value.lower() == 'nan':
                return None
                
            # Assicurati che sia numerico dopo la pulizia
            if str_value.isdigit():
                # Aggiungi padding di zeri a sinistra per raggiungere 3 cifre
                return str_value.zfill(3)
            else:
                # Se non è numerico, restituisci come stringa (gestisce casi edge)
                return str_value
        
        return tariff_series.apply(clean_single_tariff)

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pulisce e prepara i dati per l'inserimento nel database, inclusa la traduzione
        """
        logger.info("Pulizia e traduzione dati in corso...")
        
        # Crea una copia per evitare SettingWithCopyWarning
        df = df.copy()
        
        # 1. Pulisci codici tariff
        df['tariff'] = self.clean_tariff_codes(df['tariff'])
        
        # 2. Traduci le colonne testuali
        for column in self.columns_to_translate:
            if column in df.columns:
                df[column] = self.translate_column(df[column], column)
        
        # 3. Converti date
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
        
        # 4. Riempi end_date mancanti con start_date
        mask = df['end_date'].isna()
        df.loc[mask, 'end_date'] = df.loc[mask, 'start_date']
        
        # 5. Gestisci valori mancanti per le colonne stringa (ora in inglese)
        string_columns = ['client_id', 'client_type', 'client_main_group', 'tariff_position']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
        
        # 6. Assicurati che quantity sia numeric
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        
        # 7. Rimuovi eventuali duplicati
        df = df.drop_duplicates()
        
        logger.info(f"Dati puliti e tradotti: {len(df):,} record")
        return df

    def create_database_schema(self):
        """
        Crea lo schema del database con i tipi corretti
        """
        logger.info("Creazione schema database (versione inglese)...")
        
        # Crea la tabella healthcare_records
        columns_sql = []
        for col, sql_type in self.dtype_mapping.items():
            columns_sql.append(f"{col} {sql_type}")
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS healthcare_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join(columns_sql)},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        self.conn.execute("DROP TABLE IF EXISTS healthcare_records")
        self.conn.execute(create_table_sql)
        
        # Crea indici per performance
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_patient_id ON healthcare_records(patient_id)",
            "CREATE INDEX IF NOT EXISTS idx_start_date ON healthcare_records(start_date)", 
            "CREATE INDEX IF NOT EXISTS idx_tariff ON healthcare_records(tariff)",
            "CREATE INDEX IF NOT EXISTS idx_provider ON healthcare_records(healthcare_provider_id)",
            "CREATE INDEX IF NOT EXISTS idx_provider_type ON healthcare_records(healthcare_provider_type)",
            "CREATE INDEX IF NOT EXISTS idx_reason ON healthcare_records(reason_for_treatment)"
        ]
        
        for idx_sql in indices:
            self.conn.execute(idx_sql)
            
        self.conn.commit()
        logger.info("Schema database creato con successo")

    def load_csv_files(self, data_dir: str = "data", max_files: int = None) -> pd.DataFrame:
        """
        Carica tutti i file CSV con i tipi corretti
        """
        logger.info("Caricamento file CSV...")
        
        data_path = Path(data_dir)
        csv_files = sorted(data_path.glob("data_css_challenge_*.csv"))
        
        if max_files:
            csv_files = csv_files[:max_files]
        
        dataframes = []
        
        for i, csv_file in enumerate(csv_files):
            logger.info(f"Caricamento file {i+1}/{len(csv_files)}: {csv_file.name}")
            
            # Carica con tipi specificati per evitare warning
            df = pd.read_csv(
                csv_file,
                dtype=self.pandas_dtypes,
                low_memory=False
            )
            
            df['source_file'] = csv_file.name
            dataframes.append(df)
        
        # Concatena tutti i dataframe
        combined_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Caricati {len(combined_df):,} record totali da {len(csv_files)} file")
        
        return combined_df

    def insert_data_to_db(self, df: pd.DataFrame, batch_size: int = 10000):
        """
        Inserisce i dati nel database a batch
        """
        logger.info("Inserimento dati tradotti nel database...")
        
        # Prepara i dati per l'inserimento
        columns = list(self.dtype_mapping.keys())
        df_insert = df[columns].copy()
        
        # Converti date a stringa per SQLite
        for col in ['start_date', 'end_date']:
            if col in df_insert.columns:
                df_insert[col] = df_insert[col].dt.strftime('%Y-%m-%d')
        
        # Inserisci a batch per performance migliori
        total_rows = len(df_insert)
        for i in range(0, total_rows, batch_size):
            batch = df_insert.iloc[i:i+batch_size]
            batch.to_sql('healthcare_records', self.conn, if_exists='append', index=False, method='multi')
            
            logger.info(f"Inseriti {min(i+batch_size, total_rows):,}/{total_rows:,} record")
        
        self.conn.commit()
        logger.info("Inserimento completato!")

    def convert_csv_to_sql(self, data_dir: str = "data", max_files: int = None):
        """
        Processo completo di conversione CSV -> SQL con traduzione
        """
        try:
            # Connessione al database
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"Connesso al database: {self.db_path}")
            
            # 1. Crea schema
            self.create_database_schema()
            
            # 2. Carica CSV
            df = self.load_csv_files(data_dir, max_files)
            
            # 3. Pulisci e traduci dati
            df_cleaned = self.clean_data(df)
            
            # 4. Inserisci nel database
            self.insert_data_to_db(df_cleaned)
            
            # 5. Statistiche finali
            cursor = self.conn.execute("SELECT COUNT(*) FROM healthcare_records")
            total_records = cursor.fetchone()[0]
            
            logger.info(f"✅ Conversione completata!")
            logger.info(f"📊 Record totali nel database: {total_records:,}")
            
            # Mostra esempi di record tradotti
            sample_query = """
            SELECT patient_id, age, gender, reason_for_treatment, 
                   healthcare_provider_type, tariff, start_date
            FROM healthcare_records 
            LIMIT 5
            """
            sample_df = pd.read_sql_query(sample_query, self.conn)
            print("\n🔍 Esempi di record nel database (TRADOTTI IN INGLESE):")
            print(sample_df.to_string(index=False))
            
        except Exception as e:
            logger.error(f"Errore durante la conversione: {e}")
            raise
        finally:
            if self.conn:
                self.conn.close()

    def get_database_info(self):
        """
        Mostra informazioni sul database creato (in inglese)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Schema tabella
            cursor = conn.execute("PRAGMA table_info(healthcare_records)")
            schema_info = cursor.fetchall()
            
            print("\n📋 Schema tabella healthcare_records:")
            print("-" * 60)
            for col_info in schema_info:
                print(f"{col_info[1]:25} {col_info[2]:15} {'NOT NULL' if col_info[3] else ''}")
            
            # Statistiche con dati tradotti
            stats_queries = {
                "Record totali": "SELECT COUNT(*) FROM healthcare_records",
                "Pazienti unici": "SELECT COUNT(DISTINCT patient_id) FROM healthcare_records", 
                "Codici tariff unici": "SELECT COUNT(DISTINCT tariff) FROM healthcare_records",
                "Range date": """
                SELECT 
                    MIN(start_date) as min_date,
                    MAX(start_date) as max_date
                FROM healthcare_records
                """,
                "Top 5 reason_for_treatment (IN INGLESE)": """
                SELECT reason_for_treatment, COUNT(*) as count 
                FROM healthcare_records 
                GROUP BY reason_for_treatment 
                ORDER BY count DESC 
                LIMIT 5
                """,
                "Top 5 provider types (IN INGLESE)": """
                SELECT healthcare_provider_type, COUNT(*) as count 
                FROM healthcare_records 
                GROUP BY healthcare_provider_type 
                ORDER BY count DESC 
                LIMIT 5
                """
            }
            
            print("\n📊 Statistiche database (DATI TRADOTTI):")
            print("-" * 40)
            for desc, query in stats_queries.items():
                if "Top 5" in desc:
                    df = pd.read_sql_query(query, conn)
                    print(f"\n{desc}:")
                    print(df.to_string(index=False))
                else:
                    result = conn.execute(query).fetchone()
                    print(f"{desc}: {result}")
                    
        except Exception as e:
            logger.error(f"Errore nel recupero informazioni database: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    # Configurazione
    converter = HealthcareDataConverter("healthcare_data_english.db")
    
    # Converti CSV a SQL con traduzioni (puoi limitare il numero di file per test)
    print("🚀 Avvio conversione CSV -> SQL con traduzioni inglesi...")
    converter.convert_csv_to_sql()  # Rimuovi max_files per processare tutti i file
    
    # Mostra informazioni sul database creato
    converter.get_database_info()
    
    print(f"\n✅ Database inglese creato: {converter.db_path}")
    print("🌍 Tutti i dati sono ora tradotti in inglese!")
    print("🔗 Puoi ora utilizzare il database con qualsiasi strumento SQL!") 