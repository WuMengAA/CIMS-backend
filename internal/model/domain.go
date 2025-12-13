package model

import (
	"time"
)

// --- Domain Models (JSON Structure) ---

type TimeRule struct {
	WeekDay           int `json:"WeekDay"`
	WeekCountDiv      int `json:"WeekCountDiv"`
	WeekCountDivTotal int `json:"WeekCountDivTotal"`
}

type ClassInfo struct {
	SubjectId       string                 `json:"SubjectId"`
	IsChangedClass  bool                   `json:"IsChangedClass"`
	AttachedObjects map[string]interface{} `json:"AttachedObjects,omitempty"`
}

type ClassPlan struct {
	TimeLayoutId     string                 `json:"TimeLayoutId"`
	TimeRule         TimeRule               `json:"TimeRule"`
	Classes          []ClassInfo            `json:"Classes"`
	Name             string                 `json:"Name"`
	IsOverlay        bool                   `json:"IsOverlay"`
	OverlaySourceId  *string                `json:"OverlaySourceId"`
	OverlaySetupTime time.Time              `json:"OverlaySetupTime"`
	IsEnabled        bool                   `json:"IsEnabled"`
	AssociatedGroup  string                 `json:"AssociatedGroup"`
	AttachedObjects  map[string]interface{} `json:"AttachedObjects,omitempty"`
}

type TimeLayoutItem struct {
	StartSecond     string                 `json:"StartSecond"` // DateTime string
	EndSecond       string                 `json:"EndSecond"`
	TimeType        int                    `json:"TimeType"`
	IsHideDefault   bool                   `json:"IsHideDefault"`
	DefaultClassId  string                 `json:"DefaultClassId"`
	BreakName       string                 `json:"BreakName"`
	ActionSet       map[string]interface{} `json:"ActionSet,omitempty"`
	AttachedObjects map[string]interface{} `json:"AttachedObjects,omitempty"`
}

type TimeLayout struct {
	Name            string                 `json:"Name"`
	Layouts         []TimeLayoutItem       `json:"Layouts"`
	AttachedObjects map[string]interface{} `json:"AttachedObjects,omitempty"`
}

type Subject struct {
	Name            string                 `json:"Name"`
	Initial         string                 `json:"Initial"`
	TeacherName     string                 `json:"TeacherName"`
	IsOutDoor       bool                   `json:"IsOutDoor"`
	AttachedObjects map[string]interface{} `json:"AttachedObjects,omitempty"`
}

type ManagementPolicy struct {
	DisableProfileEditing           bool `json:"DisableProfileEditing"`
	DisableProfileClassPlanEditing  bool `json:"DisableProfileClassPlanEditing"`
	DisableProfileTimeLayoutEditing bool `json:"DisableProfileTimeLayoutEditing"`
	DisableProfileSubjectsEditing   bool `json:"DisableProfileSubjectsEditing"`
	DisableSettingsEditing          bool `json:"DisableSettingsEditing"`
	DisableSplashCustomize          bool `json:"DisableSplashCustomize"`
	DisableDebugMenu                bool `json:"DisableDebugMenu"`
	AllowExitManagement             bool `json:"AllowExitManagement"`
	DisableEasterEggs               bool `json:"DisableEasterEggs"`
}

// --- DB Models (Tables) ---

// CPFile stores a collection of ClassPlans (Dictionary<Guid, ClassPlan>)
type CPFile struct {
	Name      string `gorm:"primaryKey"`
	Content   string // JSON: map[string]ClassPlan
	Version   int64
	UpdatedAt time.Time
}

// TLFile stores a collection of TimeLayouts
type TLFile struct {
	Name      string `gorm:"primaryKey"`
	Content   string // JSON: map[string]TimeLayout
	Version   int64
	UpdatedAt time.Time
}

// SubFile stores a collection of Subjects
type SubFile struct {
	Name      string `gorm:"primaryKey"`
	Content   string // JSON: map[string]Subject
	Version   int64
	UpdatedAt time.Time
}

// PolicyFile stores a single Policy object
type PolicyFile struct {
	Name      string `gorm:"primaryKey"`
	Content   string // JSON: ManagementPolicy
	Version   int64
	UpdatedAt time.Time
}

// SettingsFile stores a single Settings object
type SettingsFile struct {
	Name      string `gorm:"primaryKey"`
	Content   string // JSON: map[string]interface{} (Complex settings object)
	Version   int64
	UpdatedAt time.Time
}

// Client Profile Mapping
type ClientProfile struct {
	ClientID        string `gorm:"primaryKey"`
	ClassPlan       string // Refers to CPFile.Name
	TimeLayout      string // Refers to TLFile.Name
	Subjects        string // Refers to SubFile.Name
	DefaultSettings string // Refers to SettingsFile.Name
	Policy          string // Refers to PolicyFile.Name
	UpdatedAt       time.Time
}
