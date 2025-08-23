import React, { useEffect } from 'react';

import { motion } from 'framer-motion';

const PrivacyPolicy: React.FC = () => {
    useEffect(() => {
        window.scrollTo(0, 0);
        document.title = "Privacy Policy | Beehive";
    }, []);

    return (
        <div className="min-h-screen bg-gray-100">
            <main className="pt-24 pb-16">
                <div className="container mx-auto px-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="max-w-3xl mx-auto"
                    >
                        <h1 className="text-3xl md:text-4xl font-bold mb-8 text-yellow-500">Privacy Policy</h1>

                        <div className="prose prose-yellow max-w-none">
                            <p className="text-gray-600 mb-4">Last updated: April 14, 2024</p>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Introduction</h2>
                                <p className="text-gray-700">
                                    At Beehive, protecting your privacy and securing healthcare data is our top priority. This Privacy
                                    Policy explains how we collect, use, disclose, and safeguard sensitive healthcare information when you use our platform.
                                </p>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Information We Collect</h2>
                                <p className="text-gray-700">We collect and process the following types of information:</p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>
                                        <strong>Healthcare Provider Information:</strong> Professional credentials, contact details, and organizational affiliations.
                                    </li>
                                    <li>
                                        <strong>Behavioral Health Data:</strong> De-identified and aggregated behavioral health statistics and metrics.
                                    </li>
                                    <li>
                                        <strong>Platform Usage Data:</strong> Information about how authorized users interact with our analytics tools and dashboards.
                                    </li>
                                    <li>
                                        <strong>System Logs:</strong> Technical information necessary for security and audit purposes.
                                    </li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">HIPAA Compliance</h2>
                                <p className="text-gray-700">
                                    As a platform handling sensitive healthcare information, we maintain strict HIPAA compliance:
                                </p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>End-to-end encryption for all data transmission and storage</li>
                                    <li>Regular security audits and compliance assessments</li>
                                    <li>Strict access controls and authentication measures</li>
                                    <li>Comprehensive audit trails of all data access</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Data Usage and Processing</h2>
                                <p className="text-gray-700">We use collected information for:</p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>Providing behavioral health analytics and insights</li>
                                    <li>Improving platform functionality and user experience</li>
                                    <li>Generating aggregated healthcare trends and reports</li>
                                    <li>Maintaining platform security and compliance</li>
                                    <li>Supporting healthcare research initiatives (with proper consent)</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Data Security</h2>
                                <p className="text-gray-700">
                                    We implement state-of-the-art security measures to protect your data:
                                </p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>Military-grade encryption protocols</li>
                                    <li>Multi-factor authentication</li>
                                    <li>Regular security updates and penetration testing</li>
                                    <li>Secure data centers with physical security measures</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Your Rights</h2>
                                <p className="text-gray-700">
                                    As a healthcare provider or authorized user, you have the right to:
                                </p>
                                <ul className="list-disc pl-5 text-gray-700 space-y-2 mt-3">
                                    <li>Access your organization's data and usage information</li>
                                    <li>Request corrections to inaccurate information</li>
                                    <li>Receive data exports in standard formats</li>
                                    <li>Review audit logs of data access</li>
                                </ul>
                            </section>

                            <section className="mb-8">
                                <h2 className="text-xl font-semibold mb-4 text-yellow-500">Contact Us</h2>
                                <p className="text-gray-700">
                                    For privacy-related inquiries or to exercise your rights, contact our Privacy Officer:
                                    <br />
                                    <strong>Email:</strong> <a href="mailto:privacy@beehive-health.com" className="text-yellow-600 hover:underline">privacy@beehive-health.com</a>
                                </p>
                            </section>
                        </div>
                    </motion.div>
                </div>
            </main>
        </div>
    );
};

export default PrivacyPolicy;