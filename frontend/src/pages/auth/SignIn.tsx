import { SignIn } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

const SignInPage = () => {
  const navigate = useNavigate();

  return (
    <SignIn
      appearance={{
        elements: {
          formButtonPrimary: 
            'bg-yellow-500 hover:bg-yellow-600 text-white transition-all duration-300 rounded-xl px-8 py-3 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5',
          card: 
            'bg-white shadow-none border-none',
          headerTitle: 
            'text-2xl font-bold text-gray-900 dark:text-white',
          headerSubtitle: 
            'text-gray-500 dark:text-gray-400',
          socialButtonsBlockButton: 
            'border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-all duration-200 rounded-xl shadow-sm hover:shadow transform hover:-translate-y-0.5',
          socialButtonsBlockButtonText: 
            'text-gray-600 dark:text-gray-300 font-medium',
          formFieldLabel: 
            'text-gray-700 dark:text-gray-300 font-medium',
          formFieldInput: 
            'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:border-yellow-500 dark:focus:border-yellow-500 focus:ring-4 focus:ring-yellow-500/20 dark:focus:ring-yellow-500/20 rounded-xl transition-all duration-200',
          footerActionLink: 
            'text-yellow-600 dark:text-yellow-500 hover:text-yellow-700 dark:hover:text-yellow-400 transition-colors duration-200 font-semibold',
          dividerLine: 
            'bg-gray-200 dark:bg-gray-700',
          dividerText: 
            'text-gray-400 dark:text-gray-500 bg-transparent px-4',
          formFieldInputShowPasswordButton: 
            'text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300',
          otpCodeFieldInput: 
            'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:border-yellow-500 dark:focus:border-yellow-500 focus:ring-4 focus:ring-yellow-500/20 dark:focus:ring-yellow-500/20 rounded-xl transition-all duration-200',
          footer: 
            'pb-6',
          main: 
            'px-6 pt-6',
          identityPreviewEditButton: 
            'text-yellow-600 hover:text-yellow-700 dark:text-yellow-500 dark:hover:text-yellow-400',
          formFieldSuccessText: 
            'text-green-600 dark:text-green-500',
          formFieldErrorText: 
            'text-red-600 dark:text-red-500',
          alert: 
            'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-900/50',
          alertText: 
            'text-yellow-800 dark:text-yellow-300',
          formResendCodeLink: 
            'text-yellow-600 hover:text-yellow-700 dark:text-yellow-500 dark:hover:text-yellow-400',
        },
        layout: {
          socialButtonsPlacement: "bottom",
          socialButtonsVariant: "blockButton",
        },
      }}
      routing="path"
      path="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/landing"
      redirectUrl="/sign-in"
    />
  );
};

export default SignInPage; 