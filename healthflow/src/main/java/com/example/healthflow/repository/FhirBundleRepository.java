package com.example.healthflow.repository;


import com.example.healthflow.model.FhirBundleEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface FhirBundleRepository extends JpaRepository<FhirBundleEntity, Long> {
    // Spring crée automatiquement la requête SQL pour ça :
    List<FhirBundleEntity> findByPatientId(String patientId);
}