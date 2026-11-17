package br.com.metaltech.monitoramento.controller;

import br.com.metaltech.monitoramento.dto.request.AnomaliaRequest;
import br.com.metaltech.monitoramento.dto.response.AnomaliaResponse;
import br.com.metaltech.monitoramento.service.AnomaliaService;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

import java.util.List;

@RestController 
public class AnomaliaController {
    
    private final AnomaliaService anomaliaService;

    public AnomaliaController(AnomaliaService anomaliaService) {
        this.anomaliaService = anomaliaService;
    }

    @PostMapping("/api/v1/analytics/anomalies") 
    public ResponseEntity<Void> registrar(
        @Valid @RequestBody AnomaliaRequest request
    ) {
        anomaliaService.registrar(request);
        return ResponseEntity.status(HttpStatus.CREATED).build();
    } 

    @GetMapping("/api/v1/analytics/anomalies") 
    public List<AnomaliaResponse> listarTodas() {
        return anomaliaService.listarTodas();
    }
}
