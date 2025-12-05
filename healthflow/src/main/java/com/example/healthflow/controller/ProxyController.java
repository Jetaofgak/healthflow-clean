package com.example.healthflow.controller;

import com.example.healthflow.service.FhirSyncService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/proxy")
public class ProxyController {

    private final FhirSyncService service;

    public ProxyController(FhirSyncService service) {
        this.service = service;
    }

    @PostMapping("/sync/{patientId}")
    public String syncPatient(@PathVariable String patientId) {
        return service.syncPatientData(patientId);
    }
}