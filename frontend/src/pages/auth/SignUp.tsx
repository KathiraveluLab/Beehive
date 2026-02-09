import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { saveToken } from "../../utils/auth";
import { apiFetch } from "../../utils/apiFetch";

const SignUpPage = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState<"email" | "otp" | "password" | "complete">(
    "email",
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const requestOtp = async () => {
    setLoading(true);
    setError("");

    try {
      await apiFetch("/api/auth/request-otp", {
        method: "POST",
        body: JSON.stringify({ email }),
      });

      // if apiFetch didn't throw → success
      setStep("otp");
    } catch (err: any) {
      setError(err.message || "Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    setLoading(true);
    setError("");

    try {
      await apiFetch("/api/auth/verify-otp", {
        method: "POST",
        body: JSON.stringify({ email, otp }),
      });

      // success → move ahead
      setStep("complete");
    } catch (err: any) {
      console.error("VERIFY OTP ERROR:", err);
      setError(err.message || "Invalid or expired OTP");
    } finally {
      setLoading(false);
    }
  };

  const completeSignup = async () => {
    // Email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email");
      return;
    }

    // Password length check
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    setError("");

    try {
      const data = await apiFetch("/api/auth/complete-signup", {
        method: "POST",
        body: JSON.stringify({
          email,
          username,
          password,
        }),
      });

      saveToken(data.access_token);

      // auto redirect
      data.role === "admin" ? navigate("/admin") : navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to complete signup");
    } finally {
      setLoading(false);
    }
  };

  const setPasswordAndSignup = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await apiFetch("/api/auth/set-password", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      saveToken(data.access_token);

      data.role === "admin" ? navigate("/admin") : navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };


  return (
    // Added text-gray-900 to ensure text visibility across all systems
    <div className="inline-block">
      <div className="bg-white p-8 rounded-xl shadow-xl max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
          Sign Up
        </h2>

        {error && (
          <p className="text-red-600 text-sm mb-4 text-center font-medium">
            {error}
          </p>
        )}

        <div className="space-y-4">
          {/* EMAIL STEP */}
          {step === "email" && (
            <>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
              />
              <button
                onClick={requestOtp}
                disabled={loading}
                className={`w-full py-2 rounded-md transition font-medium
    ${
      loading
        ? "bg-yellow-300 cursor-not-allowed text-gray-600"
        : "bg-yellow-400 hover:bg-yellow-600 text-black"
    }`}
              >
                {loading ? "Sending OTP..." : "Send OTP"}
              </button>
            </>
          )}

          {step === "otp" && (
            <>
              <input
                type="text"
                placeholder="Enter OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className="input"
              />
              <button
                onClick={verifyOtp}
                className="w-full bg-yellow-400 text-black py-2 rounded-md hover:bg-yellow-600 transition"
              >
                Verify OTP
              </button>
            </>
          )}

          {step === "complete" && (
            <>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input"
              />

              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
              />

              <button
                onClick={completeSignup}
                className="w-full bg-yellow-400 text-black py-2 rounded-md hover:bg-yellow-600 transition"
              >
                Create Account
              </button>
            </>
          )}

          {/* PASSWORD STEP */}
          {step === "password" && (
            <>
              <input
                type="password"
                placeholder="Create password"
                className="w-full border border-gray-300 px-3 py-2 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-amber-500 outline-none"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                onClick={setPasswordAndSignup}
                disabled={loading}
                className="w-full bg-amber-500 hover:bg-amber-600 text-white font-semibold py-2 rounded-lg transition-colors disabled:bg-amber-300"
              >
                {loading ? "Creating..." : "Create Account"}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
