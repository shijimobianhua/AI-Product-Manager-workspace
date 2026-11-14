# Optional Windows PNG rasterization. SVG generation itself is cross-platform.
param([string]$FontName = 'Microsoft YaHei')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$layout = Join-Path $root 'outputs/diagram-layout.json'
if (-not (Test-Path -LiteralPath $layout)) { throw 'Run render_diagrams.py first.' }
$figures = [IO.File]::ReadAllText($layout, [Text.Encoding]::UTF8) | ConvertFrom-Json
function ColorOf([string]$value) { return [Drawing.ColorTranslator]::FromHtml($value) }
foreach ($figure in $figures) {
  $bitmap = [Drawing.Bitmap]::new([int]$figure.width, [int]$figure.height)
  $graphics = [Drawing.Graphics]::FromImage($bitmap)
  $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  foreach ($e in $figure.elements) {
    if ($e.type -eq 'rect') {
      $brush = [Drawing.SolidBrush]::new((ColorOf $e.fill))
      $pen = [Drawing.Pen]::new((ColorOf $e.stroke), 1)
      $graphics.FillRectangle($brush, [single]$e.x, [single]$e.y, [single]$e.w, [single]$e.h)
      $graphics.DrawRectangle($pen, [single]$e.x, [single]$e.y, [single]$e.w, [single]$e.h)
      $brush.Dispose(); $pen.Dispose()
    } elseif ($e.type -eq 'text') {
      $style = if ($e.bold) { [Drawing.FontStyle]::Bold } else { [Drawing.FontStyle]::Regular }
      $font = [Drawing.Font]::new($FontName, [single]$e.size, $style, [Drawing.GraphicsUnit]::Pixel)
      $brush = [Drawing.SolidBrush]::new((ColorOf $e.color))
      $graphics.DrawString([string]$e.value, $font, $brush, [single]$e.x, [single]$e.y)
      $font.Dispose(); $brush.Dispose()
    } elseif ($e.type -eq 'line') {
      $pen = [Drawing.Pen]::new((ColorOf $e.color), 4)
      $graphics.DrawLine($pen, [single]$e.x1, [single]$e.y1, [single]$e.x2, [single]$e.y2)
      $pen.Dispose()
    } elseif ($e.type -eq 'polygon') {
      $points = [Drawing.PointF[]]@($e.points | ForEach-Object { [Drawing.PointF]::new([single]$_[0], [single]$_[1]) })
      $brush = [Drawing.SolidBrush]::new((ColorOf $e.fill)); $graphics.FillPolygon($brush, $points); $brush.Dispose()
    }
  }
  $target = Join-Path $root ('90-assets/diagrams/' + $figure.name + '.png')
  $bitmap.Save($target, [Drawing.Imaging.ImageFormat]::Png)
  $graphics.Dispose(); $bitmap.Dispose()
}
Write-Output ('Rendered {0} PNG diagrams.' -f $figures.Count)
