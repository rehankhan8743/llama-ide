import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-blue-600 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">🦙</span>
          <h1 className="text-xl font-bold">llama-ide</h1>
        </div>
        <div className="flex space-x-4">
          <Link to="/" className="hover:underline">Editor</Link>
          <Link to="/playground" className="hover:underline">Playground</Link>
          <Link to="/settings" className="hover:underline">Settings</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
