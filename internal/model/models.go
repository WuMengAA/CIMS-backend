package model

import (
	"time"
)

// Client represents a connected or registered client
type Client struct {
	ID            string `gorm:"primaryKey"` // UUID
	Name          string
	Status        string // online, offline
	IP            string
	LastHeartbeat time.Time
	CreatedAt     time.Time
	UpdatedAt     time.Time
}

// PreRegister represents a pre-registered client configuration
type PreRegister struct {
	ID              string `gorm:"primaryKey"` // Client UUID
	Name            string
	ClassPlan       string
	TimeLayout      string
	Subjects        string
	DefaultSettings string
	Policy          string
	CreatedAt       time.Time
}

// Setting represents server-wide settings
type Setting struct {
	Key       string `gorm:"primaryKey"`
	Value     string
	UpdatedAt time.Time
}
