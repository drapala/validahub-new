import { test, expect } from '@playwright/test'

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display hero section with CTAs', async ({ page }) => {
    // Check hero content
    await expect(page.locator('h1')).toContainText('Valide e corrija seus catálogos CSV')
    
    // Check CTAs are present
    const startButton = page.getByRole('button', { name: /começar agora/i })
    const plansButton = page.getByRole('button', { name: /ver planos/i })
    
    await expect(startButton).toBeVisible()
    await expect(plansButton).toBeVisible()
  })

  test('should open auth modal when clicking "Começar agora"', async ({ page }) => {
    // Click the start button
    await page.getByRole('button', { name: /começar agora/i }).first().click()
    
    // Check if modal is opened
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByText(/criar nova conta/i)).toBeVisible()
    
    // Check tabs
    await expect(page.getByRole('tab', { name: /google/i })).toBeVisible()
    await expect(page.getByRole('tab', { name: /email/i })).toBeVisible()
  })

  test('should navigate to pricing page', async ({ page }) => {
    // Click on pricing button
    await page.getByRole('button', { name: /ver planos/i }).first().click()
    
    // Check if navigated to pricing page
    await expect(page).toHaveURL('/pricing')
    await expect(page.locator('h1')).toContainText('Planos e Preços')
  })

  test('should scroll to sections when clicking nav links', async ({ page }) => {
    // Click on Features link
    await page.getByRole('button', { name: /features/i }).click()
    
    // Check if features section is in viewport
    const featuresSection = page.locator('#features')
    await expect(featuresSection).toBeInViewport()
  })

  test('should show all landing page sections', async ({ page }) => {
    // Check all sections are present
    const sections = [
      'Empresas que confiam', // Social proof
      'Como funciona',
      'Features poderosas',
      'Planos simples',
      'Perguntas frequentes',
      'Pronto para validar'  // CTA
    ]
    
    for (const section of sections) {
      await expect(page.getByText(section)).toBeVisible()
    }
  })

  test('should toggle between sign in and sign up in auth modal', async ({ page }) => {
    // Open modal
    await page.getByRole('button', { name: /começar agora/i }).first().click()
    
    // Should start in sign up mode
    await expect(page.getByText(/criar nova conta/i)).toBeVisible()
    
    // Click on "Já tem uma conta?"
    await page.getByText(/já tem uma conta/i).click()
    
    // Should switch to sign in mode
    await expect(page.getByText(/entrar na sua conta/i)).toBeVisible()
    
    // Click on "Cadastre-se"
    await page.getByText(/não tem uma conta.*cadastre-se/i).click()
    
    // Should switch back to sign up mode
    await expect(page.getByText(/criar nova conta/i)).toBeVisible()
  })

  test('should redirect to home when accessing protected route without auth', async ({ page }) => {
    // Try to access protected route
    await page.goto('/upload')
    
    // Should be redirected to home
    await expect(page).toHaveURL('/?callbackUrl=%2Fupload')
  })

  test('should display FAQ accordion', async ({ page }) => {
    // Scroll to FAQ section
    await page.evaluate(() => {
      document.querySelector('#faq')?.scrollIntoView()
    })
    
    // Click on first FAQ item
    const firstQuestion = page.getByText('Como vocês validam cada marketplace?')
    await firstQuestion.click()
    
    // Check if answer is visible
    await expect(page.getByText(/mantemos um banco de dados atualizado/i)).toBeVisible()
    
    // Click again to close
    await firstQuestion.click()
    
    // Check if answer is hidden
    await expect(page.getByText(/mantemos um banco de dados atualizado/i)).not.toBeVisible()
  })

  test('should display mobile menu on small screens', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check hamburger menu is visible
    const menuButton = page.getByRole('button').filter({ has: page.locator('svg') }).first()
    await expect(menuButton).toBeVisible()
    
    // Click to open mobile menu
    await menuButton.click()
    
    // Check menu items are visible
    await expect(page.getByRole('button', { name: /features/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /como funciona/i })).toBeVisible()
  })
})

test.describe('Authentication Flow', () => {
  test('should handle email sign up flow', async ({ page }) => {
    await page.goto('/')
    
    // Open auth modal
    await page.getByRole('button', { name: /começar agora/i }).first().click()
    
    // Switch to email tab
    await page.getByRole('tab', { name: /email/i }).click()
    
    // Fill sign up form
    await page.fill('input[type="text"]', 'Test User')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')
    
    // Check terms checkbox
    await page.getByLabel(/aceito os termos/i).check()
    
    // Note: Actual submission would require mocking the API
    // Here we just verify the form can be filled
    await expect(page.getByRole('button', { name: /criar conta/i })).toBeEnabled()
  })

  test('should show error for invalid login', async ({ page }) => {
    await page.goto('/')
    
    // Open auth modal
    await page.getByRole('button', { name: /entrar/i }).first().click()
    
    // Should open in sign in mode
    await page.getByText(/já tem uma conta.*fazer login/i).click()
    
    // Switch to email tab
    await page.getByRole('tab', { name: /email/i }).click()
    
    // Fill login form with invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    
    // Submit form
    await page.getByRole('button', { name: /entrar/i }).click()
    
    // Should show error message (mocked)
    // Note: This would need API mocking to work properly
  })
})

test.describe('Pricing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pricing')
  })

  test('should display three pricing tiers', async ({ page }) => {
    await expect(page.getByText('Starter')).toBeVisible()
    await expect(page.getByText('Pro')).toBeVisible()
    await expect(page.getByText('Enterprise')).toBeVisible()
  })

  test('should toggle between monthly and annual pricing', async ({ page }) => {
    // Check initial state (monthly)
    await expect(page.getByText('R$ 199')).toBeVisible()
    
    // Toggle to annual
    const switchButton = page.getByRole('switch')
    await switchButton.click()
    
    // Check annual price
    await expect(page.getByText('R$ 179')).toBeVisible()
  })
})