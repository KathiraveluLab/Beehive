import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { saveToken, getUserRole } from "../../utils/auth";
import { apiFetch } from "../../utils/apiFetch";
import { GoogleLogin } from "@react-oauth/google";

const SignInPage = () => {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false); // State for visibility
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });

      const token = data.access_token;
      saveToken(token);

      const role = getUserRole();
      navigate(role === "admin" ? "/admin" : "/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="inline-block">
      <div className="bg-white p-8 rounded-xl shadow-xl max-w-md">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Sign In</h2>
          <p className="text-gray-500 mt-2">
            Welcome back! Please enter your details.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm text-center">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Enter your username"
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 bg-white focus:ring-2 focus:ring-yellow-500 outline-none transition-all"
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-700 block mb-1.5">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"} // Toggle type
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-gray-900 bg-white focus:ring-2 focus:ring-yellow-500 outline-none transition-all"
              />
              <button
                type="button" // Important: prevents form submission
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-gray-500 hover:text-yellow-600 uppercase"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-yellow-500 hover:bg-yellow-600 active:scale-[0.98] text-white font-bold py-3.5 rounded-xl shadow-md transition-all disabled:opacity-70"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-white px-2 text-gray-500">or</span>
          </div>
        </div>

        {/* Google Sign In */}
        <GoogleLogin
          onSuccess={async (credentialResponse) => {
            try {
              const data = await apiFetch("/api/auth/google", {
                method: "POST",
                body: JSON.stringify({
                  id_token: credentialResponse.credential
                }),
              });

              saveToken(data.access_token);
              navigate(data.role === "admin" ? "/admin" : "/dashboard");
            } catch (err) {
              setError("Google sign-in failed");
            }
          }}
          onError={() => setError("Google sign-in failed")}
          useOneTap={false}
        />

        <p className="text-center text-sm text-gray-500 mt-8">
          Don't have an account?{" "}
          <a
            href="/signup"
            className="text-yellow-600 font-semibold hover:underline"
          >
            Contact Admin
          </a>
        </p>
      </div>
    </div>
  );
};

export default SignInPage;
