import { useState, useEffect, useCallback } from 'react';
import { UserCircleIcon, LockClosedIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import { apiUrl } from '../utils/api';
import { getToken, saveToken } from '../utils/auth';
import toast from 'react-hot-toast';

interface UserProfile {
  username: string;
  email: string;
  provider: string;
  role: string;
  created_at: string | null;
  has_password: boolean;
}

const Settings = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const authFetch = useCallback((path: string, options: RequestInit = {}) => {
    return fetch(apiUrl(path), {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
        ...options.headers,
      },
    });
  }, []);

  useEffect(() => {
    authFetch('/api/auth/me')
      .then((res) => res.json())
      .then((data) => setProfile(data))
      .catch(() => toast.error('Failed to load profile'))
      .finally(() => setProfileLoading(false));
  }, [authFetch]);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setPasswordLoading(true);
    try {
      const res = await authFetch('/api/auth/change-password', {
        method: 'PATCH',
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to change password');
      }
      // The server ends sessions opened with the old password and returns a fresh token.
      if (data.access_token) {
        saveToken(data.access_token);
      }
      toast.success('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const joinedDate = profile?.created_at
    ? new Date(profile.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null;

  return (
    <div className="py-10 px-4">
      <div className="max-w-2xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold">Account Settings</h1>

        {/* Profile card */}
        <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <UserCircleIcon className="h-6 w-6 text-yellow-400" />
            <h2 className="text-xl font-semibold">Profile</h2>
          </div>

          {profileLoading ? (
            <div className="space-y-3 animate-pulse">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-64" />
            </div>
          ) : profile ? (
            <dl className="divide-y divide-gray-100 dark:divide-gray-700">
              <div className="py-3 flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Username</dt>
                <dd className="text-sm font-semibold">{profile.username}</dd>
              </div>
              <div className="py-3 flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Email</dt>
                <dd className="text-sm">{profile.email}</dd>
              </div>
              <div className="py-3 flex justify-between">
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Sign-in method</dt>
                <dd>
                  {profile.provider === 'google' ? (
                    <span className="inline-flex items-center gap-1.5 text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2.5 py-1 rounded-full">
                      <ShieldCheckIcon className="h-3.5 w-3.5" />
                      Google
                    </span>
                  ) : (
                    <span className="text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 px-2.5 py-1 rounded-full">
                      Email &amp; Password
                    </span>
                  )}
                </dd>
              </div>
              {joinedDate && (
                <div className="py-3 flex justify-between">
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Member since</dt>
                  <dd className="text-sm">{joinedDate}</dd>
                </div>
              )}
            </dl>
          ) : (
            <p className="text-sm text-red-500">Could not load profile.</p>
          )}
        </section>

        {/* Change password card — hidden for OAuth users without a password */}
        {profile && profile.has_password && (
          <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-6">
              <LockClosedIcon className="h-6 w-6 text-yellow-400" />
              <h2 className="text-xl font-semibold">Change Password</h2>
            </div>

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="current-password">
                  Current password
                </label>
                <input
                  id="current-password"
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="new-password">
                  New password
                </label>
                <input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="confirm-password">
                  Confirm new password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={passwordLoading}
                  className="bg-yellow-400 hover:bg-yellow-500 disabled:opacity-50 text-black font-semibold py-2 px-6 rounded-lg transition-colors duration-200"
                >
                  {passwordLoading ? 'Saving…' : 'Update Password'}
                </button>
              </div>
            </form>
          </section>
        )}

        {/* Info for OAuth users */}
        {profile && !profile.has_password && (
          <section className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-3 mb-2">
              <LockClosedIcon className="h-6 w-6 text-yellow-400" />
              <h2 className="text-xl font-semibold">Password</h2>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Your account uses Google sign-in. Password management is handled by Google.
            </p>
          </section>
        )}
      </div>
    </div>
  );
};

export default Settings;
