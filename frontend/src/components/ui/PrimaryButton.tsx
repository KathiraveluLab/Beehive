import { motion } from "framer-motion";

interface PrimaryButtonProps {
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}

const PrimaryButton = ({ onClick, children, className = "" }: PrimaryButtonProps) => {
  return (
    <motion.button
      onClick={onClick}
      className={`bg-primary text-black px-8 py-3 rounded-full hover:bg-primary-dark transition-all shadow-lg hover:shadow-xl font-semibold ${className}`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  );
};

export default PrimaryButton;
