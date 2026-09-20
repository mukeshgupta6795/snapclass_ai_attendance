import streamlit as st
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_results import show_attendance_results

@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write("Record audio of student saying I am present")

    audio_data = None

    audio_data = st.audio_input("Record classroom audio")
    if st.button("Analyze audio" , width='stretch' , type='primary'):
        with st.spinner('Processing audio data...'):
            enrolled_res = supabase.table('subject_students').select('* , students(*)').eq('subject_id' ,selected_subject_id ).execute()
            enrolled_students = enrolled_res.data
            # st.write(enrolled_students)
            
            if not enrolled_students:
                st.warning('No students enrolled in this cource')
                return

            candidates_dict = {
                s['students']['student_id'] : s['students']['voice_embedding']
                for s in enrolled_students if s['students'].get('voice_embedding')
            }
            # st.write(type(candidates_dict))

            if not candidates_dict:
                st.error('Students voice not enrolled')
                return

            if audio_data is None:
                st.warning("Please record your voice first.")
                return

            audio_bytes = audio_data.read()

            detected_scores = process_bulk_audio(audio_bytes , candidates_dict)
            results , attendance_to_log = [] , []
            
            currrent_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") 

            for node in enrolled_students:
                student = node["students"]
                score = detected_scores.get(student['student_id'] , 0.0)
                is_present =bool(score>0)
                # st.write(student)

                results.append({
                    "Name" : student['name'],
                    "ID" : student['student_id'],
                    "Source": score if is_present else "-",
                    "Status" : "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    "student_id" : student['student_id'],
                    'subject_id' : selected_subject_id,
                    'timestamp' : currrent_timestamp,
                    'is_present':bool(is_present) 
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()

        df_results , logs = st.session_state.voice_attendance_results
        show_attendance_results(df_results , logs)

            
           
