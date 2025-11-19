# Runbook - follow-watch

## İlk deploy sonrası kontroller
1. Kubernetes pod'larının hepsinin `READY` olduğundan emin ol (kubectl get pods -n followwatch).
2. Receiver endpoint'ine test imzalı bir webhook gönder (imza için WEBHOOK_SECRET kullan).
3. events_log tablosunda event görünüyor mu kontrol et.
4. Worker kuyruğunu kontrol et; işlenmiş event'ler processed=true olmalı.
5. Publisher servisi publish endpoint'ini çağırıyor mu; X API token'ını kontrol et.

## Yaygın olaylar
- **Queue backlog yükseliyor**: worker replicas arttır, consumer logs kontrol et.
- **Publisher rate limit hatası**: publish servisi rate-limit header'larını okuyup exponential backoff uygulasın; geçici olarak publishing durdur.

## Geri dönüş (rollback)
- Son başarılı image tag'ine rollback: kubectl set image deployment/<deploy> <container>=ghcr.io/yourorg/<image>:<tag>
