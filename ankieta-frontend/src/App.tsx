import {useEffect} from 'react';
import { useState } from 'react';
import LogisticsSurvey from './components/LogisticsSurvey/LogisticsSurvey';
import "survey-core/survey-core.css";
import "./theme/index.css";

const App = () => {
  const [schema, setSchema] = useState(null);

  useEffect(() => {
    fetch('/survey_schema.json')
      .then(r => r.json())
      .then(setSchema);
  }, []);

  if (!schema) return <div className="loading">Loading...</div>;

  return (
    <main style={{ width: "100%", height: "100%" }}>
      <LogisticsSurvey schema={schema} />
    </main>
  );
};

export default App;