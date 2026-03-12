// components/Survey.tsx
import { Model } from 'survey-core';

const surveyJson = { /* ... */ }

export default function SurveyComponent() {
  const survey = new Model(surveyJson);
  console.log(survey);
  return "...";
}
