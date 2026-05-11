"""
main.py – App-wide constants and configuration for DharmaSetu.
"""

APP_TITLE    = "DharmaSetu: AI Legal Research Assistant"
APP_SUBTITLE = "Educational Legal Research Tool | Not Legal Advice"
APP_FOOTER   = "Developed by Jogu Yugandar | DharmaSetu Project | AI Legal Assistant"

# Supported user roles and their explanation styles
ROLES = {
    "Student": "simplified, easy-to-understand language suitable for a law student",
    "Lawyer": "professional case-analysis style with references to legal provisions",
    "Judge": "formal, objective legal language focusing on principles and precedents",
}

# Optional context inputs for personalised legal analysis
GENDERS   = ["Prefer not to say", "Male", "Female", "Other"]
RELIGIONS = ["Prefer not to say", "Hindu", "Muslim", "Christian", "Sikh", "Other"]

# Supported languages
LANGUAGES = ["English", "Hindi", "Telugu"]

# Example queries shown as quick-access buttons
EXAMPLE_QUERIES = [
    "Neighbour harassment case",
    "Verbal abuse towards women",
    "Physical assault after provocation",
    "Is delayed evidence valid in court?",
]

# Fixed scenarios for each example query button.
# When a button is clicked, this full text is sent to the AI instead of the short label,
# so the AI analyses a specific known scenario rather than inventing one.
QUERY_SCENARIOS = {
    "Neighbour harassment case": (
        "Two neighbouring families have been in a long-standing dispute over a shared boundary wall. "
        "The neighbour repeatedly plays loud music late at night, throws garbage near the complainant's "
        "door, and has verbally abused the complainant's family members on multiple occasions. "
        "The complainant has a video recording of one such incident and two witnesses."
    ),
    "Verbal abuse towards women": (
        "A man used abusive and vulgar language toward a woman in a public place. "
        "He made derogatory remarks about her character in front of bystanders. "
        "The incident was recorded on a mobile phone by a witness. "
        "The woman filed a complaint with the police the same day."
    ),
    "Physical assault after provocation": (
        "During a heated argument over a parking dispute, one person slapped and punched the other. "
        "The victim claims the accused attacked without warning. The accused claims he was provoked "
        "by abusive language. There are two eyewitnesses and CCTV footage from a nearby shop. "
        "The victim sustained minor injuries and obtained a medical report."
    ),
    "Is delayed evidence valid in court?": (
        "A complainant filed a case six months after the incident occurred. "
        "The key evidence is a video recording that was submitted to police one month after the incident. "
        "The accused argues the delay in filing and submitting evidence makes it unreliable. "
        "The complainant states the delay was due to fear of retaliation."
    ),
}

# Pool of demo cases — one is picked randomly each time "Try Demo Case" is clicked
DEMO_CASES = [
    (
        "Two neighboring families had a dispute. A boy used abusive and vulgar language "
        "toward two girls. The girls' father became angry and physically assaulted the boy. "
        "The issue was initially resolved between families. After one month, the boy's "
        "grandmother reported the incident to police and submitted a video recording as evidence."
    ),
    (
        "A female employee at a private company complained that her male manager repeatedly "
        "made inappropriate comments about her appearance and sent unwanted messages on her "
        "personal phone. She reported the matter to HR but no action was taken for two months. "
        "She then filed a complaint with the Internal Complaints Committee."
    ),
    (
        "After the death of their father, two brothers disputed the ownership of an ancestral "
        "property. The elder brother claimed exclusive rights based on a will, while the younger "
        "brother argued the will was forged. A handwriting expert was hired to examine the document. "
        "The property is located in a village and was never registered."
    ),
    (
        "A retired government employee received a phone call from someone claiming to be a bank "
        "official. The caller convinced him to share his OTP to verify his account. Within "
        "minutes, Rs 1.5 lakh was transferred from his account. He filed a complaint at the "
        "cyber crime cell the next day with call records and bank transaction screenshots."
    ),
    (
        "A woman alleged that her in-laws harassed her for additional dowry six months after "
        "marriage. She claimed her husband and mother-in-law physically assaulted her on two "
        "occasions. She left the matrimonial home and filed a complaint. Her husband denies "
        "the allegations and claims she left voluntarily due to a personal dispute."
    ),
    (
        "A motorcyclist was hit by a speeding car at a busy intersection. The car driver fled "
        "the scene. A bystander recorded the car's number plate on his mobile phone. The "
        "injured motorcyclist was hospitalised for three weeks. Police traced the car owner "
        "but he claims the car was stolen on that day and filed a theft complaint the next morning."
    ),
]
