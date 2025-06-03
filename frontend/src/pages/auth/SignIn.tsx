import { SignIn } from '@clerk/clerk-react';

const SignInPage = () => {
  return (
    <div className="w-full">
      <SignIn
        appearance={{
          elements: {
            formButtonPrimary: 'bg-yellow-400 hover:bg-yellow-500 transition-colors duration-200',
            card: 'bg-white dark:bg-gray-800 shadow-md rounded-lg',
            headerTitle: 'text-gray-900 dark:text-white',
            headerSubtitle: 'text-gray-600 dark:text-gray-400',
            socialButtonsBlockButton: 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200',
            socialButtonsBlockButtonText: 'text-gray-600 dark:text-gray-400',
            formFieldLabel: 'text-gray-700 dark:text-gray-300',
            formFieldInput: 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-colors duration-200',
            footerActionLink: 'text-yellow-400 hover:text-yellow-500 transition-colors duration-200',
          },
        }}
        routing="path"
        path="/sign-in"
      />
    </div>
  );
};

export default SignInPage; 