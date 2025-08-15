'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { AlertCircle, CheckCircle, AlertTriangle, Info, Loader2 } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

export default function ValidateRowPage() {
  const [marketplace, setMarketplace] = useState('MERCADO_LIVRE')
  const [category, setCategory] = useState('none')
  const [autoFix, setAutoFix] = useState(true)
  const [rowData, setRowData] = useState(`{
  "sku": "",
  "title": "Produto Teste",
  "price": -10,
  "stock": -5,
  "category": "InvalidCategory",
  "status": "wrong_status"
}`)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const exampleData = {
    errors: {
      sku: "",
      title: "",
      price: -99.99,
      stock: -10,
      category: "InvalidCategory",
      status: "wrong_status"
    },
    valid: {
      sku: "SKU-12345",
      title: "Notebook Dell Inspiron",
      price: 2999.99,
      stock: 10,
      category: "Electronics",
      status: "active"
    },
    partial: {
      sku: "SKU-789",
      title: "Mouse Gamer",
      price: 0,
      stock: null,
      category: ""
    }
  }

  const validateRow = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const parsedData = JSON.parse(rowData)
      
      const params = new URLSearchParams({
        marketplace,
        auto_fix: autoFix.toString(),
        row_number: '1'
      })
      
      if (category && category !== 'none') {
        params.append('category', category)
      }

      const response = await fetch(`http://localhost:3001/api/v1/validate_row?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedData)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('JSON inválido. Verifique o formato dos dados.')
      } else {
        setError(err instanceof Error ? err.message : 'Erro ao validar')
      }
    } finally {
      setLoading(false)
    }
  }

  const loadExample = (type: keyof typeof exampleData) => {
    setRowData(JSON.stringify(exampleData[type], null, 2))
  }

  return (
    <div className="container mx-auto py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Validação de Linha Única</h1>
        <p className="text-muted-foreground">
          Teste a validação de uma única linha de dados com o rule engine YAML
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Configuration Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configuração</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="marketplace">Marketplace</Label>
                <Select value={marketplace} onValueChange={setMarketplace}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-950 border-zinc-800">
                    <SelectItem value="MERCADO_LIVRE">Mercado Livre</SelectItem>
                    <SelectItem value="SHOPEE">Shopee</SelectItem>
                    <SelectItem value="AMAZON">Amazon</SelectItem>
                    <SelectItem value="MAGALU">Magalu</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Categoria (opcional)</Label>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione uma categoria" />
                  </SelectTrigger>
                  <SelectContent className="bg-zinc-950 border-zinc-800">
                    <SelectItem value="none">Nenhuma</SelectItem>
                    <SelectItem value="ELETRONICOS">Eletrônicos</SelectItem>
                    <SelectItem value="MODA">Moda</SelectItem>
                    <SelectItem value="CASA">Casa</SelectItem>
                    <SelectItem value="ESPORTE">Esporte</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="auto-fix"
                  checked={autoFix}
                  onCheckedChange={setAutoFix}
                />
                <Label htmlFor="auto-fix">Auto-correção ativada</Label>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Dados da Linha (JSON)</CardTitle>
              <CardDescription>
                Insira os dados em formato JSON para validação
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadExample('errors')}
                >
                  Com Erros
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadExample('valid')}
                >
                  Válido
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadExample('partial')}
                >
                  Parcial
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setRowData('{}')}
                >
                  Limpar
                </Button>
              </div>

              <Textarea
                value={rowData}
                onChange={(e) => setRowData(e.target.value)}
                className="font-mono min-h-[200px]"
                placeholder='{"sku": "", "title": "Produto"}'
              />

              <Button
                onClick={validateRow}
                disabled={loading}
                className="w-full"
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {loading ? 'Validando...' : 'Validar Linha'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Results Panel */}
        <div className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    Status da Validação
                    {result.has_errors ? (
                      <Badge variant="destructive">Com Erros</Badge>
                    ) : result.has_warnings ? (
                      <Badge variant="warning">Com Avisos</Badge>
                    ) : (
                      <Badge variant="success">Válido</Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <AlertCircle className="h-4 w-4 text-destructive" />
                      <span>Erros: {result.validation_items?.filter((i: any) => 
                        i.status === 'ERROR').length || 0}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <AlertTriangle className="h-4 w-4 text-warning" />
                      <span>Avisos: {result.validation_items?.filter((i: any) => 
                        i.status === 'WARNING').length || 0}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <CheckCircle className="h-4 w-4 text-success" />
                      <span>Correções: {result.validation_items?.reduce((acc: number, i: any) => 
                        acc + (i.corrections?.length || 0), 0) || 0}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Errors */}
              {result.validation_items?.some((i: any) => i.errors?.length > 0) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-destructive" />
                      Erros Encontrados
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {result.validation_items?.map((item: any, idx: number) => 
                      item.errors?.map((error: any, errIdx: number) => (
                        <Alert key={`${idx}-${errIdx}`} variant="destructive">
                          <div className="space-y-1">
                            <div className="font-semibold">{error.code}</div>
                            {error.field && (
                              <Badge variant="outline" className="mb-1">
                                Campo: {error.field}
                              </Badge>
                            )}
                            <div className="text-sm">{error.message}</div>
                            {error.value !== undefined && (
                              <div className="text-xs text-muted-foreground">
                                Valor atual: <code>{JSON.stringify(error.value)}</code>
                              </div>
                            )}
                            {error.expected !== undefined && (
                              <div className="text-xs text-muted-foreground">
                                Esperado: <code>{JSON.stringify(error.expected)}</code>
                              </div>
                            )}
                          </div>
                        </Alert>
                      ))
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Corrections */}
              {result.validation_items?.some((i: any) => i.corrections?.length > 0) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-success" />
                      Correções Aplicadas
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {result.validation_items?.map((item: any, idx: number) => 
                      item.corrections?.map((correction: any, corrIdx: number) => (
                        <Alert key={`${idx}-${corrIdx}`} className="border-success">
                          <div className="space-y-1">
                            <div className="font-semibold">
                              {correction.field}
                            </div>
                            <div className="text-sm space-y-1">
                              <div>
                                <span className="text-muted-foreground">De:</span>{' '}
                                <code>{JSON.stringify(correction.original_value)}</code>
                              </div>
                              <div>
                                <span className="text-muted-foreground">Para:</span>{' '}
                                <code className="text-success">
                                  {JSON.stringify(correction.corrected_value)}
                                </code>
                              </div>
                              <div className="text-xs text-muted-foreground">
                                Tipo: {correction.correction_type}
                                {correction.confidence && 
                                  ` • Confiança: ${(correction.confidence * 100).toFixed(0)}%`}
                              </div>
                            </div>
                          </div>
                        </Alert>
                      ))
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Data Comparison */}
              {result.auto_fix_applied && result.fixed_row && (
                <Card>
                  <CardHeader>
                    <CardTitle>Comparação de Dados</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Original</Label>
                      <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                        {JSON.stringify(result.original_row, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <Label className="text-sm font-medium mb-2 block">Corrigido</Label>
                      <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                        {JSON.stringify(result.fixed_row, null, 2)}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Raw Response */}
              <Card>
                <CardHeader>
                  <CardTitle>Resposta Completa</CardTitle>
                  <CardDescription>
                    Resposta raw da API para debug
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}