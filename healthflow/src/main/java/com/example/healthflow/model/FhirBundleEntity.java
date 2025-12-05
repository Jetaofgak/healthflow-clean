package com.example.healthflow.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "fhir_bundles")
@Data // Lombok génère getters/setters
public class FhirBundleEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String patientId;

    @Column(columnDefinition = "TEXT") // Pour stocker le gros JSON
    private String rawJson;

    private LocalDateTime syncDate;

    @PrePersist
    public void prePersist() {
        this.syncDate = LocalDateTime.now();
    }
}
