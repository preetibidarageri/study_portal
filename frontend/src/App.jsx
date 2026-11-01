import "./App.css";
import Home from "./pages/Home/Home";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import StudentLogin from "./pages/StudentLogin/StudentLogin";
import Register from "./pages/Register/Register";
import TeacherLogin from "./pages/TeacherLogin/TeacherLogin";
import StudentDashboard from "./pages/StudentDashboard/StudentDashboard";
import Subjects from "./pages/Subjects/Subjects";
function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/register" element={<Register />} />
          <Route path="/teacher/login" element={<TeacherLogin />} />
          <Route path="/dashboard" element={<StudentDashboard />} />
          <Route path="/subjects" element={<Subjects />} />
        </Routes>
      </BrowserRouter>{" "}
    </>
  );
}

export default App;
