import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // <-- import navigate
import "./person.css";

interface Props {
  onComplete: (data: any) => void;
}

const Person: React.FC<Props> = ({ onComplete }) => {
  const navigate = useNavigate(); // <-- initialize navigate

  const [problem, setProblem] = useState("");
  const [style, setStyle] = useState("");
  const [time, setTime] = useState("");

  const handleSubmit = () => {
    const data = { problem, style, time };
    console.log("User Preferences:", data);

    onComplete(data); // send to parent if needed
    navigate("/dashboard"); // <-- go to dashboard
  };

  const renderOptions = (
    options: string[],
    selected: string,
    setSelected: (val: string) => void
  ) => {
    return options.map((option) => (
      <button
        key={option}
        className={`option-btn ${selected === option ? "selected" : ""}`}
        onClick={() => setSelected(option)}
      >
        {option}
      </button>
    ));
  };

  return (
    <div className="person-container">
      <div className="card">
        <h1 className="title">Let’s personalize your experience</h1>

        {/* Question 1 */}
        <div className="question">
          <p>What slows you down?</p>
          <div className="options">
            {renderOptions(
              [
                "I procrastinate",
                "I get overwhelmed",
                "I don’t know where to start",
                "I get distracted",
              ],
              problem,
              setProblem
            )}
          </div>
        </div>

        {/* Question 2 */}
        <div className="question">
          <p>How do you prefer to work?</p>
          <div className="options">
            {renderOptions(
              ["Small quick tasks", "Bigger focused tasks", "Doesn’t matter"],
              style,
              setStyle
            )}
          </div>
        </div>

        {/* Question 3 */}
        <div className="question">
          <p>How much time do you usually have?</p>
          <div className="options">
            {renderOptions(
              ["5–10 mins", "15–30 mins", "1+ hour"],
              time,
              setTime
            )}
          </div>
        </div>

        <button className="start-btn" onClick={handleSubmit}>
          Get Started
        </button>
      </div>
    </div>
  );
};

export default Person;
