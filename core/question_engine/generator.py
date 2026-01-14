'''
generator.py: Generate the final questions, send this to the frontend for display.
- this is where explainability lives
- sample output:
{
  "question": "...",
  "based_on": "Resume project X",
  "intent": "depth probe"
}
- optional: display this for every question in the frontend, the reasoning, which chunk was retrieved and so on
'''