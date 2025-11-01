import { useState } from 'react'

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Login:', { email, password })
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="w-[400px] h-[500px] flex flex-col items-center pt-[60px] pb-[60px] px-[40px]">
        {/* Title */}
        <h1 className="text-[32px] font-bold text-[#1a1a1a] leading-[38.72px]">
          Welcome Back
        </h1>
        
        {/* Subtitle */}
        <p className="text-base text-[#808080] leading-[19.36px] mt-5">
          Sign in to your account
        </p>
        
        {/* Form */}
        <form onSubmit={handleLogin} className="w-[320px] mt-5 space-y-5">
          {/* Email Field */}
          <div className="h-12 bg-[#f5f5f5] rounded-lg px-4 flex items-center">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full bg-transparent text-sm text-[#666666] placeholder:text-[#666666] focus:outline-none"
            />
          </div>
          
          {/* Password Field */}
          <div className="h-12 bg-[#f5f5f5] rounded-lg px-4 flex items-center">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full bg-transparent text-sm text-[#666666] placeholder:text-[#666666] focus:outline-none"
            />
          </div>
          
          {/* Login Button */}
          <button
            type="submit"
            className="w-full h-12 bg-[#3366ff] rounded-lg flex items-center justify-center text-white text-base font-semibold hover:bg-[#2d5ae8] transition-colors"
          >
            Login
          </button>
        </form>
        
        {/* Sign Up Button */}
        <button className="w-[320px] h-12 border-2 border-[#3366ff] rounded-lg flex items-center justify-center text-[#3366ff] text-base font-semibold hover:bg-blue-50 transition-colors mt-5">
          Sign Up
        </button>
      </div>
    </div>
  )
}

export default App
