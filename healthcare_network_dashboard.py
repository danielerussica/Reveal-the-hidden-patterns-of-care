import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from streamlit_agraph import agraph, Node, Edge, Config
import warnings
import hashlib
import traceback
import json
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Healthcare Treatment Flow Network",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
    }
    .stSelectbox label {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class HealthcareNetworkDashboard:
    def __init__(self):
        self.data = None
        self.network_data = None
        self.filtered_data = None
        
        # German to English translation mappings
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
        
        # Column name translations
        self.column_translations = {
            'patient_id': 'Patient ID',
            'age': 'Age',
            'gender': 'Gender',
            'reason_for_treatment': 'Treatment Reason',
            'healthcare_provider_type': 'Provider Type',
            'healthcare_provider_main_group': 'Provider Group',
            'client_type': 'Client Type',
            'client_main_group': 'Client Group',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'from': 'From',
            'to': 'To',
            'weight': 'Transitions',
            'provider': 'Provider',
            'unique_patients': 'Unique Patients',
            'total_visits': 'Total Visits'
        }
    
    def translate_text(self, text):
        """Translate German text to English using the translation dictionary"""
        if pd.isna(text) or text == '':
            return text
        
        # Handle exact matches first
        if str(text) in self.translations:
            return self.translations[str(text)]
        
        # Handle partial matches for complex provider types
        text_str = str(text)
        for german_term, english_term in self.translations.items():
            if german_term in text_str:
                text_str = text_str.replace(german_term, english_term)
        
        return text_str
    
    def translate_dataframe(self, df):
        """Apply translations to relevant columns in the dataframe"""
        df_translated = df.copy()
        
        # Columns that need translation
        translation_columns = [
            'age', 'reason_for_treatment', 'healthcare_provider_type', 
            'healthcare_provider_main_group', 'client_type', 'client_main_group'
        ]
        
        for col in translation_columns:
            if col in df_translated.columns:
                df_translated[col] = df_translated[col].apply(self.translate_text)
        
        return df_translated
    
    def translate_dataframe_for_display(self, df):
        """Translate both content and column headers for display"""
        df_display = self.translate_dataframe(df).copy()
        
        # Translate column headers
        new_columns = {}
        for col in df_display.columns:
            if col in self.column_translations:
                new_columns[col] = self.column_translations[col]
            else:
                new_columns[col] = col
        
        df_display = df_display.rename(columns=new_columns)
        return df_display
        
    def load_data(self, sample_size=50000, files_to_load=3):
        """Load and prepare healthcare data"""
        try:
            data_dir = "data"
            sample_dfs = []
            
            # Show progress
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            status_text.text(f'Starting data load: {sample_size:,} records from {files_to_load} files...')
            
            for i in range(files_to_load):
                try:
                    status_text.text(f'Loading file {i+1}/{files_to_load}: data_css_challenge_{i}.csv...')
                    file_path = f"{data_dir}/data_css_challenge_{i}.csv"
                    
                    # Load with explicit parameters
                    df_sample = pd.read_csv(
                        file_path, 
                        nrows=sample_size//files_to_load,
                        low_memory=False
                    )
                    df_sample['source_file'] = i
                    sample_dfs.append(df_sample)
                    
                    progress_bar.progress((i + 1) / files_to_load)
                    status_text.text(f'Loaded {len(df_sample):,} records from file {i+1}')
                    
                except Exception as file_error:
                    st.error(f"Error loading file {i}: {str(file_error)}")
                    continue
            
            if not sample_dfs:
                st.error("No data files could be loaded!")
                return None
            
            status_text.text('Combining and processing data...')
            data = pd.concat(sample_dfs, ignore_index=True)
            
            # Clean and prepare data
            status_text.text('Processing dates and cleaning data...')
            data['start_date'] = pd.to_datetime(data['start_date'], errors='coerce')
            data['end_date'] = pd.to_datetime(data['end_date'], errors='coerce')
            data['treatment_duration_days'] = (data['end_date'] - data['start_date']).dt.days
            data['year_month'] = data['start_date'].dt.to_period('M').astype(str)
            
            # Apply translations to German text
            status_text.text('Translating German text to English...')
            data = self.translate_dataframe(data)
            
            # Clean provider names for better visualization
            data['provider_clean'] = data['healthcare_provider_type'].apply(
                lambda x: x[:30] + '...' if len(str(x)) > 30 else str(x)
            )
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            progress_container.empty()
            
            return data
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.error("Traceback:")
            st.code(traceback.format_exc())
            return None
    
    def create_unique_id(self, text):
        """Create unique ID from text using hash to avoid duplicates"""
        return hashlib.md5(str(text).encode()).hexdigest()[:8]
    
    def create_network_data(self, data, min_transitions=2):
        """Create network graph data from patient transitions"""
        try:
            # Get patient transitions
            transitions = []
            
            st.text("Analyzing patient transitions...")
            
            for patient_id, group in data.groupby('patient_id'):
                if len(group) > 1:  # Only patients with multiple visits
                    group_sorted = group.sort_values('start_date')
                    providers = group_sorted['healthcare_provider_type'].tolist()
                    ages = group_sorted['age'].tolist()
                    genders = group_sorted['gender'].tolist()
                    reasons = group_sorted['reason_for_treatment'].tolist()
                    dates = group_sorted['start_date'].tolist()
                    
                    for i in range(len(providers) - 1):
                        transitions.append({
                            'from': providers[i],
                            'to': providers[i + 1],
                            'patient_id': patient_id,
                            'age': ages[i],
                            'gender': genders[i],
                            'reason': reasons[i],
                            'from_date': dates[i],
                            'to_date': dates[i + 1] if i + 1 < len(dates) else None
                        })
            
            if not transitions:
                st.warning("No patient transitions found (no patients with multiple visits)")
                return None, None, None
            
            st.text(f"Found {len(transitions)} transitions, creating network...")
            transitions_df = pd.DataFrame(transitions)
            
            # Count transitions and filter by minimum threshold
            edge_counts = transitions_df.groupby(['from', 'to']).agg({
                'patient_id': 'count',
                'age': lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown',
                'gender': lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown',
                'reason': lambda x: x.mode().iloc[0] if not x.mode().empty else 'Unknown'
            }).reset_index()
            
            edge_counts.columns = ['from', 'to', 'weight', 'common_age', 'common_gender', 'common_reason']
            edge_counts = edge_counts[edge_counts['weight'] >= min_transitions]
            
            if len(edge_counts) == 0:
                st.warning(f"No connections with ≥{min_transitions} transitions found")
                return None, None, None
            
            # Get node statistics
            all_providers = set(edge_counts['from'].unique()) | set(edge_counts['to'].unique())
            node_stats = []
            
            for provider in all_providers:
                provider_data = data[data['healthcare_provider_type'] == provider]
                unique_patients = provider_data['patient_id'].nunique()
                avg_age = provider_data['age'].mode().iloc[0] if not provider_data['age'].mode().empty else 'Unknown'
                common_reason = provider_data['reason_for_treatment'].mode().iloc[0] if not provider_data['reason_for_treatment'].mode().empty else 'Unknown'
                provider_group = provider_data['healthcare_provider_main_group'].mode().iloc[0] if not provider_data['healthcare_provider_main_group'].mode().empty else 'Unknown'
                
                node_stats.append({
                    'provider': provider,
                    'unique_patients': unique_patients,
                    'total_visits': len(provider_data),
                    'avg_age': avg_age,
                    'common_reason': common_reason,
                    'provider_group': provider_group,
                    'provider_id': self.create_unique_id(provider)  # Create unique ID
                })
            
            node_stats_df = pd.DataFrame(node_stats)
            
            st.text("Network created successfully!")
            
            return edge_counts, node_stats_df, transitions_df
            
        except Exception as e:
            st.error(f"Error creating network: {str(e)}")
            st.code(traceback.format_exc())
            return None, None, None
    
    def create_network_graph(self, edges_df, nodes_df, layout_type="spring"):
        """Create interactive network graph using streamlit-agraph"""
        try:
            # Create nodes with unique IDs
            nodes = []
            node_id_map = {}
            
            for _, node in nodes_df.iterrows():
                unique_id = node['provider_id']  # Use the unique ID we created
                node_id_map[node['provider']] = unique_id
                
                size = min(50, max(15, node['unique_patients'] / 5))  # Scale node size
                
                # Color nodes by provider group
                color_map = {
                    'Hospitals': '#FF6B6B',
                    'Doctors': '#4ECDC4',
                    'Laboratories': '#45B7D1',
                    'Nursing Homes': '#96CEB4',
                    'Unknown': '#FFEAA7'
                }
                color = color_map.get(node['provider_group'], '#DDA0DD')
                
                # Create clean label
                label = node['provider'][:25] + "..." if len(node['provider']) > 25 else node['provider']
                
                # Create safe title without problematic characters
                title = f"Provider: {node['provider'][:50]}\nPatients: {node['unique_patients']}\nVisits: {node['total_visits']}\nGroup: {node['provider_group']}"
                
                nodes.append(
                    Node(
                        id=unique_id,  # Use unique ID
                        label=label,
                        size=size,
                        color=color,
                        title=title
                    )
                )
            
            # Create edges using the mapped IDs
            edges = []
            for _, edge in edges_df.iterrows():
                source_id = node_id_map.get(edge['from'])
                target_id = node_id_map.get(edge['to'])
                
                if source_id and target_id:  # Only create edge if both nodes exist
                    # Create safe title without problematic characters
                    title = f"Transitions: {edge['weight']}\nAge: {edge['common_age']}\nGender: {edge['common_gender']}"
                    
                    edges.append(
                        Edge(
                            source=source_id,
                            target=target_id,
                            width=min(8, max(2, edge['weight'] / 5)),  # Scale edge width
                            color='#95A5A6',
                            title=title
                        )
                    )
            
            # Configure the graph
            config = Config(
                width=1200,
                height=600,
                directed=True,
                physics=True,
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#F7CA18",
                collapsible=False
            )
            
            return nodes, edges, config
            
        except Exception as e:
            st.error(f"Error creating network graph: {str(e)}")
            return [], [], None
    
    def create_plotly_network(self, edges_df, nodes_df):
        """Create directed network graph using Plotly with arrows"""
        try:
            # Create NetworkX graph
            G = nx.from_pandas_edgelist(
                edges_df, 
                source='from', 
                target='to', 
                edge_attr=['weight'],
                create_using=nx.DiGraph()  # Use DiGraph for directed graph
            )
            
            # Add node attributes
            node_attrs = nodes_df.set_index('provider').to_dict('index')
            nx.set_node_attributes(G, node_attrs)
            
            # Calculate layout
            pos = nx.spring_layout(G, k=1.5, iterations=50)
            
            # Create edge traces with arrows for directed graph
            edge_x = []
            edge_y = []
            edge_info = []
            annotations = []  # For arrows
            
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                # Calculate arrow position (75% along the edge)
                arrow_x = x0 + 0.75 * (x1 - x0)
                arrow_y = y0 + 0.75 * (y1 - y0)
                
                # Calculate arrow direction
                dx = x1 - x0
                dy = y1 - y0
                length = np.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    # Normalize direction vector
                    dx_norm = dx / length
                    dy_norm = dy / length
                    
                    # Add arrow annotation
                    annotations.append(
                        dict(
                            x=arrow_x,
                            y=arrow_y,
                            ax=arrow_x - 0.02 * dx_norm,
                            ay=arrow_y - 0.02 * dy_norm,
                            xref='x', yref='y',
                            axref='x', ayref='y',
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1.5,
                            arrowwidth=min(3, max(1, edge[2]['weight'] / 10)),
                            arrowcolor='#666666',
                            standoff=0
                        )
                    )
                
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_info.append(f"From: {edge[0]}<br>To: {edge[1]}<br>Transitions: {edge[2]['weight']}")
            
            # Create edge trace (lines without arrows, arrows added via annotations)
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            )
            
            # Create node traces
            node_x = []
            node_y = []
            node_info = []
            node_colors = []
            node_sizes = []
            
            color_map = {
                'Hospitals': '#FF6B6B',
                'Doctors': '#4ECDC4',
                'Laboratories': '#45B7D1',
                'Nursing Homes': '#96CEB4',
                'Unknown': '#FFEAA7'
            }
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                node_data = node_attrs.get(node, {})
                node_info.append(
                    f"Provider: {node}<br>"
                    f"Unique Patients: {node_data.get('unique_patients', 'N/A')}<br>"
                    f"Total Visits: {node_data.get('total_visits', 'N/A')}<br>"
                    f"Provider Group: {node_data.get('provider_group', 'Unknown')}"
                )
                
                provider_group = node_data.get('provider_group', 'Unknown')
                node_colors.append(color_map.get(provider_group, '#DDA0DD'))
                node_sizes.append(min(30, max(8, node_data.get('unique_patients', 10) / 5)))
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[node[:15] + '...' if len(node) > 15 else node for node in G.nodes()],
                textposition="middle center",
                textfont=dict(size=8),
                hovertext=node_info,
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                showlegend=False
            )
            
            # Create the figure with arrows
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Healthcare Provider Network (Directed)',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=annotations + [dict(
                        text="Arrows show direction of patient flow between providers",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="gray", size=10)
                    )],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='white'
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating Plotly network: {str(e)}")
            return None
    
    def run_dashboard(self):
        # Header
        st.title("🏥 Healthcare Treatment Flow Network Dashboard")
        st.markdown("Explore patient treatment journeys and provider relationships through interactive network visualization")
        
        # Initialize session state for data
        if 'dashboard_data' not in st.session_state:
            st.session_state.dashboard_data = None
            st.session_state.data_loaded = False
        
        # Sidebar filters
        st.sidebar.title("🔍 Filters & Settings")
        
        # Load data section
        with st.sidebar:
            st.subheader("Data Loading")
            sample_size = st.slider("Sample Size", 10000, 200000, 50000, step=10000)
            files_to_load = st.slider("Number of Files to Load", 1, 5, 3)
            
            if st.button("Load Data", type="primary"):
                try:
                    # Clear any existing data
                    st.session_state.dashboard_data = None
                    st.session_state.data_loaded = False
                    
                    # Show loading message
                    with st.spinner(f'Loading {sample_size:,} records from {files_to_load} files...'):
                        loaded_data = self.load_data(sample_size, files_to_load)
                    
                    if loaded_data is not None:
                        st.session_state.dashboard_data = loaded_data
                        st.session_state.data_loaded = True
                        st.success(f"✅ Successfully loaded {len(loaded_data):,} records!")
                        st.rerun()  # Refresh the page
                    else:
                        st.error("❌ Failed to load data")
                        
                except Exception as e:
                    st.error(f"❌ Error during data loading: {str(e)}")
                    st.code(traceback.format_exc())
        
        # Use session state data
        self.data = st.session_state.dashboard_data
        
        if self.data is None or not st.session_state.data_loaded:
            st.info("👈 Please load data using the sidebar controls")
            st.markdown("""
            ### Quick Start:
            1. **Set Sample Size**: Start with 50,000 records for good performance
            2. **Choose Files**: 3 files provide good data variety  
            3. **Click Load Data**: Wait for processing to complete
            4. **Apply Filters**: Explore different demographic and provider filters
            
            ### Debug Info:
            - Session state data loaded: {data_loaded}
            - Data object exists: {data_exists}
            """.format(
                data_loaded=st.session_state.data_loaded,
                data_exists=self.data is not None
            ))
            return
        
        # Show data summary
        st.sidebar.success(f"✅ Data loaded: {len(self.data):,} records")
        st.sidebar.info(f"📊 Unique patients: {self.data['patient_id'].nunique():,}")
        
        # Main filters
        with st.sidebar:
            st.subheader("Network Filters")
            
            # Age filter
            age_options = ['All'] + sorted([age for age in self.data['age'].unique() if pd.notna(age)])
            selected_age = st.selectbox("Age Group", age_options)
            
            # Gender filter  
            gender_options = ['All'] + sorted([gender for gender in self.data['gender'].dropna().unique()])
            selected_gender = st.selectbox("Gender", gender_options)
            
            # Reason filter
            reason_options = ['All'] + sorted([reason for reason in self.data['reason_for_treatment'].dropna().unique()])
            selected_reason = st.selectbox("Treatment Reason", reason_options)
            
            # Provider group filter
            provider_group_options = ['All'] + sorted([group for group in self.data['healthcare_provider_main_group'].dropna().unique()])
            selected_provider_group = st.selectbox("Provider Group", provider_group_options)
            
            # Network settings
            st.subheader("Network Settings")
            min_transitions = st.slider("Minimum Transitions", 1, 20, 3, help="Filter out weak connections")
            visualization_type = st.radio("Visualization Type", ["Plotly Network (Directed)", "Interactive Network"])
        
        # Apply filters
        filtered_data = self.data.copy()
        
        if selected_age != 'All':
            filtered_data = filtered_data[filtered_data['age'] == selected_age]
        if selected_gender != 'All':
            filtered_data = filtered_data[filtered_data['gender'] == selected_gender]
        if selected_reason != 'All':
            filtered_data = filtered_data[filtered_data['reason_for_treatment'] == selected_reason]
        if selected_provider_group != 'All':
            filtered_data = filtered_data[filtered_data['healthcare_provider_main_group'] == selected_provider_group]
        
        # Show filtered data info
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Filtered Data:**")
        st.sidebar.markdown(f"Records: {len(filtered_data):,}")
        st.sidebar.markdown(f"Patients: {filtered_data['patient_id'].nunique():,}")
        
        # Create network data
        with st.spinner('Creating network...'):
            edges_df, nodes_df, transitions_df = self.create_network_data(filtered_data, min_transitions)
        
        if edges_df is None or len(edges_df) == 0:
            st.warning("⚠️ No network connections found with current filters.")
            st.markdown("**Suggestions:**")
            st.markdown("- Reduce minimum transitions (try 1-2)")
            st.markdown("- Broaden demographic filters (try 'All')")
            st.markdown("- Increase sample size")
            st.markdown("- Load more files")
            
            # Show some basic stats about filtered data
            if len(filtered_data) > 0:
                st.subheader("📊 Filtered Data Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Records", len(filtered_data))
                    st.metric("Unique Patients", filtered_data['patient_id'].nunique())
                with col2:
                    multi_visit = filtered_data.groupby('patient_id').size()
                    st.metric("Multi-visit Patients", (multi_visit > 1).sum())
                    st.metric("Avg Visits/Patient", f"{multi_visit.mean():.1f}")
            return
        
        # Main dashboard layout
        st.subheader("📈 Network Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", f"{filtered_data['patient_id'].nunique():,}")
        with col2:
            st.metric("Provider Types", f"{len(nodes_df):,}")
        with col3:
            st.metric("Transitions", f"{edges_df['weight'].sum():,}")
        with col4:
            avg_transitions = len(transitions_df) / transitions_df['patient_id'].nunique() if len(transitions_df) > 0 else 0
            st.metric("Avg Transitions/Patient", f"{avg_transitions:.1f}")
        
        # Network visualization
        st.subheader("🔗 Treatment Flow Network")
        
        if visualization_type == "Interactive Network":
            try:
                nodes, edges, config = self.create_network_graph(edges_df, nodes_df)
                
                if len(nodes) == 0 or len(edges) == 0:
                    st.warning("No nodes or edges to display. Try adjusting your filters.")
                else:
                    st.markdown(f"**Network size:** {len(nodes)} providers, {len(edges)} connections")
                    
                    # Handle the return value more safely to avoid JSON parse errors
                    try:
                        return_value = agraph(nodes=nodes, edges=edges, config=config)
                        
                        if return_value and isinstance(return_value, dict):
                            st.subheader("Selected Node Details")
                            
                            # Find the corresponding node data
                            if 'nodes' in return_value and return_value['nodes']:
                                selected_node_id = return_value['nodes'][0]
                                
                                # Find node details from our data
                                selected_node_data = None
                                for _, node_row in nodes_df.iterrows():
                                    if node_row['provider_id'] == selected_node_id:
                                        selected_node_data = {
                                            'Provider': node_row['provider'],
                                            'Unique Patients': node_row['unique_patients'],
                                            'Total Visits': node_row['total_visits'],
                                            'Provider Group': node_row['provider_group'],
                                            'Common Age': node_row['avg_age'],
                                            'Common Reason': node_row['common_reason']
                                        }
                                        break
                                
                                if selected_node_data:
                                    st.json(selected_node_data)
                                else:
                                    st.info("Node details not found")
                            else:
                                st.info("Click on a node to see details")
                                
                    except Exception as json_error:
                        st.warning("Interactive network loaded, but node selection details may not display properly.")
                        st.info(f"Technical details: {str(json_error)}")
                        # Still show the network even if click handling has issues
                        agraph(nodes=nodes, edges=edges, config=config)
                        
            except Exception as e:
                st.error(f"Error creating interactive network: {str(e)}")
                st.info("Falling back to Plotly visualization...")
                fig = self.create_plotly_network(edges_df, nodes_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        else:
            fig = self.create_plotly_network(edges_df, nodes_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Top Provider Connections")
            if len(edges_df) > 0:
                top_edges = edges_df.nlargest(10, 'weight')[['from', 'to', 'weight']]
                # Truncate long provider names for display
                top_edges['from'] = top_edges['from'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
                top_edges['to'] = top_edges['to'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
                # Translate column headers
                top_edges_display = self.translate_dataframe_for_display(top_edges)
                st.dataframe(top_edges_display, use_container_width=True)
            else:
                st.info("No connections to display")
        
        with col2:
            st.subheader("🏥 Most Active Providers")
            if len(nodes_df) > 0:
                top_nodes = nodes_df.nlargest(10, 'unique_patients')[['provider', 'unique_patients', 'total_visits']]
                # Truncate long provider names for display
                top_nodes['provider'] = top_nodes['provider'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
                # Translate column headers
                top_nodes_display = self.translate_dataframe_for_display(top_nodes)
                st.dataframe(top_nodes_display, use_container_width=True)
            else:
                st.info("No providers to display")
        
        # Provider group distribution
        if len(nodes_df) > 0:
            st.subheader("📈 Provider Group Distribution")
            fig_dist = px.pie(
                nodes_df, 
                names='provider_group', 
                values='unique_patients',
                title="Patient Distribution by Provider Group"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
            # Edge weight distribution
            st.subheader("🔗 Transition Frequency Distribution")
            fig_edges = px.histogram(
                edges_df, 
                x='weight', 
                nbins=20,
                title="Distribution of Transition Frequencies"
            )
            st.plotly_chart(fig_edges, use_container_width=True)
        
        # Download options
        st.subheader("💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Network Edges"):
                csv = edges_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="network_edges.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Download Node Statistics"):
                csv = nodes_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="node_statistics.csv",
                    mime="text/csv"
                )

# Main execution
if __name__ == "__main__":
    dashboard = HealthcareNetworkDashboard()
    dashboard.run_dashboard() 